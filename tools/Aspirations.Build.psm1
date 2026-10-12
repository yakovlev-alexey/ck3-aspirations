Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$script:Utf8 = [Text.UTF8Encoding]::new($false, $true)
$script:Families = @('vengeance', 'holding_recovery', 'personal_bond')

function Assert-ContainedPath {
    param([string]$Path, [string]$Root)
    $absolute = [IO.Path]::GetFullPath($Path)
    $parent = [IO.Path]::GetFullPath($Root).TrimEnd([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar)
    if (-not $absolute.StartsWith($parent + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Path escapes approved root: $Path"
    }
    return $absolute
}
function Assert-NoReparsePath {
    param([string]$Path)
    $current = [IO.Path]::GetFullPath($Path)
    while ($current) {
        if (Test-Path -LiteralPath $current) {
            $item = Get-Item -LiteralPath $current -Force
            if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "Reparse point is not allowed: $current" }
        }
        $parent = [IO.Path]::GetDirectoryName($current)
        if ($parent -eq $current) { break }
        $current = $parent
    }
}
function Get-RepositoryRoot {
    param([string]$RepositoryRoot)
    $root = [IO.Path]::GetFullPath($RepositoryRoot)
    Assert-NoReparsePath $root
    if (-not [IO.Directory]::Exists($root)) { throw 'Repository root must already exist.' }
    return $root
}
function Assert-RelativePath {
    param([string]$Path)
    if ([IO.Path]::IsPathRooted($Path) -or $Path -match '[:\\]' -or $Path -match '(^|/)(\.{1,2}|)(/|$)') {
        throw "Unsafe relative path: $Path"
    }
}
function Get-SafeFiles {
    param([string]$Root)
    Assert-NoReparsePath $Root
    if (-not (Test-Path -LiteralPath $Root)) { return }
    if (-not [IO.Directory]::Exists($Root)) { throw "Expected a directory: $Root" }
    $pending = [Collections.Generic.Stack[string]]::new()
    $pending.Push($Root)
    while ($pending.Count) {
        foreach ($item in Get-ChildItem -LiteralPath $pending.Pop() -Force) {
            if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "Reparse point is not allowed: $($item.FullName)" }
            Assert-ContainedPath $item.FullName $Root | Out-Null
            if ($item.PSIsContainer) { $pending.Push($item.FullName) } else { $item.FullName }
        }
    }
}
function Get-RelativeName {
    param([string]$Root, [string]$Path)
    return [IO.Path]::GetRelativePath($Root, $Path).Replace('\', '/')
}
function Write-Utf8Text {
    param([string]$Path, [string]$Content)
    [IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($Path)) | Out-Null
    [IO.File]::WriteAllText($Path, $Content, $script:Utf8)
}
function Get-ContentHash {
    param([string]$Path)
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}
function Test-Documentation {
    param([string]$Root)
    $required = @('README.md','AGENTS.md','docs/design.md','docs/repository.md','docs/modding-notes.md','packaging/INSTALL.md','packaging/CREDITS.md')
    foreach ($module in @('core') + @($script:Families | ForEach-Object { "stories/$_" })) {
        $required += "src/$module/SPEC.md", "src/$module/tests/scenarios.md"
        $spec = Join-Path $Root "src/$module/SPEC.md"
        Assert-NoReparsePath $spec
        if (-not [IO.File]::Exists($spec)) { throw "Missing module SPEC: src/$module/SPEC.md" }
        if ([IO.File]::ReadAllText($spec) -notmatch '\]\(tests/scenarios\.md(?:#[^)]+)?\)') { throw "SPEC must link to tests/scenarios.md: $module" }
    }
    foreach ($relative in $required) {
        $path = Join-Path $Root $relative
        Assert-NoReparsePath $path
        if (-not [IO.File]::Exists($path)) { throw "Missing required documentation: $relative" }
        foreach ($match in [regex]::Matches([IO.File]::ReadAllText($path), '\]\(([^)]+)\)')) {
            $link = $match.Groups[1].Value.Split('#')[0]
            if (-not $link -or $link -match '^[a-zA-Z][a-zA-Z0-9+.-]*:') { continue }
            $linkedPath = Assert-ContainedPath (Join-Path ([IO.Path]::GetDirectoryName($path)) $link) $Root
            Assert-NoReparsePath $linkedPath
            if (-not (Test-Path -LiteralPath $linkedPath)) { throw "Broken documentation link in ${relative}: $link" }
        }
    }
    $stories = Join-Path $Root 'src/stories'
    Assert-NoReparsePath $stories
    foreach ($entry in Get-ChildItem -LiteralPath $stories -Force) {
        if (-not $entry.PSIsContainer -or $entry.Name -cnotin $script:Families) { throw "Unapproved story module: $($entry.Name)" }
        Assert-NoReparsePath $entry.FullName
    }
}
function Get-Descriptor {
    param([string]$Root, [ValidateSet('dev','release')][string]$Profile)
    $path = Join-Path $Root 'packaging/descriptor.mod'
    Assert-NoReparsePath $path
    if (-not [IO.File]::Exists($path)) { throw 'Missing packaging/descriptor.mod' }
    $text = [IO.File]::ReadAllText($path, $script:Utf8).Replace("`r`n", "`n")
    if ($text -match '(?im)^\s*(path|archive)\s*=') { throw 'Portable descriptor must not contain path or archive metadata.' }
    $allowedKeys = @('name','version','supported_version','tags','remote_file_id','picture')
    foreach ($field in [regex]::Matches($text, '(?m)^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=')) {
        if ($field.Groups[1].Value -cnotin $allowedKeys) { throw "Unrecognized portable descriptor field: $($field.Groups[1].Value)" }
    }
    $fields = @{}
    foreach ($key in @('name','version','supported_version','remote_file_id','picture')) {
        $matches = [regex]::Matches($text, '(?m)^\s*' + $key + '\s*=\s*"([^"\r\n]+)"\s*(?:#.*)?$')
        if ($matches.Count -gt 1) { throw "Duplicate descriptor field: $key" }
        if ($matches.Count -eq 1) { $fields[$key] = $matches[0].Groups[1].Value }
        elseif ($text -match ('(?m)^\s*' + $key + '\s*=')) { throw "Malformed descriptor field: $key" }
    }
    foreach ($key in @('name','version','supported_version')) { if (-not $fields.ContainsKey($key)) { throw "Missing descriptor field: $key" } }
    if ($fields.name -ne 'Aspirations') { throw 'Release descriptor name must be Aspirations.' }
    if ($fields.version -notmatch '^\d+\.\d+\.\d+(?:-[A-Za-z0-9.-]+)?$') { throw 'Descriptor version must be a portable semantic version.' }
    if ($fields.supported_version -notmatch '^\d+\.\d+\.(?:\d+|\*)$') { throw 'Invalid supported_version.' }
    if ($text -notmatch '(?s)\btags\s*=\s*\{\s*"[^"\r\n]+"') { throw 'Descriptor must have at least one tag.' }
    if ($fields.ContainsKey('remote_file_id')) {
        $id = $fields.remote_file_id
        if ($id -notmatch '^[1-9][0-9]{5,19}$' -or $id -match '^([0-9])\1+$' -or $id -in @('123456','123456789','1234567890','12345678901234567890')) {
            throw 'remote_file_id must be an actual published item ID, never a placeholder.'
        }
    }
    if ($fields.ContainsKey('picture')) { Assert-RelativePath $fields.picture }
    if ($Profile -eq 'dev') {
        $text = [regex]::Replace($text, '(?m)^\s*name\s*=.*$', 'name="Aspirations (Development)"')
        $text = [regex]::Replace($text, '(?m)^\s*remote_file_id\s*=.*\n?', '')
    }
    return [pscustomobject]@{ Text = $text.TrimEnd() + "`n"; Version = $fields.version; Picture = $(if ($fields.ContainsKey('picture')) { $fields.picture } else { $null }) }
}
function Get-AssemblyEntries {
    param([string]$Root, [string]$Profile)
    Test-Documentation $Root
    $entries = [Collections.Generic.List[object]]::new()
    $destinations = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
    foreach ($module in @('core') + @($script:Families | ForEach-Object { "stories/$_" })) {
        $roots = @("src/$module/game")
        if ($Profile -eq 'dev') { $roots += "src/$module/tests/game" }
        foreach ($moduleRoot in $roots) {
            $absolute = Join-Path $Root $moduleRoot
            foreach ($file in @(Get-SafeFiles $absolute)) {
                $relative = Get-RelativeName $absolute $file
                Assert-RelativePath $relative
                if (-not $destinations.Add($relative)) { throw "Destination collision (case insensitive): $relative" }
                $entries.Add([pscustomobject]@{ Source = Get-RelativeName $Root $file; Destination = $relative; Hash = Get-ContentHash $file })
            }
        }
    }
    $descriptor = Get-Descriptor $Root $Profile
    if (-not $destinations.Add('descriptor.mod')) { throw 'Destination collision: descriptor.mod' }
    $entries.Add([pscustomobject]@{ Source = 'packaging/descriptor.mod'; Destination = 'descriptor.mod'; Hash = $null })
    if ($descriptor.Picture) {
        if (-not $destinations.Add($descriptor.Picture)) { throw "Destination collision: $($descriptor.Picture)" }
        $picture = Assert-ContainedPath (Join-Path $Root "packaging/$($descriptor.Picture)") (Join-Path $Root 'packaging')
        Assert-NoReparsePath $picture
        if (-not [IO.File]::Exists($picture)) { throw 'Missing descriptor preview image.' }
        $entries.Add([pscustomobject]@{ Source = "packaging/$($descriptor.Picture)"; Destination = $descriptor.Picture; Hash = Get-ContentHash $picture })
    }
    $sorted = @($entries | Sort-Object -Property Destination -CaseSensitive -Culture '')
    return [pscustomobject]@{ Entries = $sorted; Descriptor = $descriptor }
}
function Test-NativeContent {
    param([string]$ModRoot, [string]$Profile, [object]$Descriptor)
    $identifiers = [Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
    foreach ($file in @(Get-SafeFiles $ModRoot)) {
        $relative = Get-RelativeName $ModRoot $file
        Assert-RelativePath $relative
        if ($relative -eq 'descriptor.mod' -or ($Descriptor.Picture -and $relative -ceq $Descriptor.Picture)) { continue }
        if ($relative -notmatch '^(common|events|localization|gfx)/' -or $relative -match '(^|/)\.' -or $relative -match '\.(md|ps1|psm1|zip|exe|dll|ck3|log)$') { throw "Unexpected native package file: $relative" }
        if ($relative.StartsWith('localization/')) {
            if ($relative -notmatch '^localization/english/[^/]+_l_english\.yml$') { throw "English localization only: $relative" }
            $bytes = [IO.File]::ReadAllBytes($file)
            if ($bytes.Length -lt 3 -or $bytes[0] -ne 239 -or $bytes[1] -ne 187 -or $bytes[2] -ne 191) { throw "Localization requires UTF-8 BOM: $relative" }
            $text = $script:Utf8.GetString($bytes, 3, $bytes.Length - 3)
            if ($text -notmatch '\A(?:[ \t]*#.*\r?\n|\s*\r?\n)*l_english:\s*(?:#.*)?(?:\r?\n|$)') { throw "Missing l_english header: $relative" }
            foreach ($match in [regex]::Matches($text, '(?m)^\s*(asp_[A-Za-z0-9_]+):\d*\s')) {
                if (-not $identifiers.Add('localization:' + $match.Groups[1].Value)) { throw "Duplicate mod-owned localization ID: $($match.Groups[1].Value)" }
            }
            continue
        }
        if ($relative -match '^(common|events)/' -and $relative -notmatch '\.txt$') { throw "Native scripts must use .txt: $relative" }
        if ([IO.Path]::GetExtension($file) -notin @('.txt','.asset','.gfx')) { continue }
        $text = [IO.File]::ReadAllText($file, $script:Utf8)
        if ($Profile -eq 'release' -and ($relative -match '(?i)debug' -or $text -match '\basp_test_')) { throw "Dev fixture in release content: $relative" }
        # Focused definition scan: quoted strings/comments removed; only top-level asp_ assignments (blocks or scalar values).
        # Native hooks, nested invocations and namespaces may legitimately repeat.
        $clean = [regex]::Replace($text, '"(?:\\.|[^"\\])*"|#[^\r\n]*', ' ')
        $depth = 0
        foreach ($token in [regex]::Matches($clean, '\b(asp_[A-Za-z0-9_]+(?:\.[0-9]+)?)\s*=|[{}]')) {
            if ($token.Value -eq '{') { $depth++ }
            elseif ($token.Value -eq '}') { $depth--; if ($depth -lt 0) { throw "Unbalanced script braces: $relative" } }
            elseif ($depth -eq 0 -and -not $identifiers.Add('script:' + $token.Groups[1].Value)) { throw "Duplicate mod-owned script ID: $($token.Groups[1].Value)" }
        }
        if ($depth -ne 0) { throw "Unbalanced script braces: $relative" }
    }
    if ([IO.File]::ReadAllText((Join-Path $ModRoot 'descriptor.mod')) -cne $Descriptor.Text) { throw 'Output descriptor differs from validated profile metadata.' }
}
function Get-GeneratedPaths {
    param([string]$Root, [string]$Profile)
    $build = Assert-ContainedPath (Join-Path $Root '.build') $Root
    $profileRoot = Assert-ContainedPath (Join-Path $build $Profile) $build
    $mod = Assert-ContainedPath (Join-Path $profileRoot 'mod') $build
    foreach ($path in @($build, $profileRoot, $mod, (Join-Path $profileRoot 'manifest.json'))) { Assert-NoReparsePath $path }
    @(Get-SafeFiles $mod) | Out-Null
    return [pscustomobject]@{ Build = $build; Profile = $profileRoot; Mod = $mod; Manifest = Join-Path $profileRoot 'manifest.json' }
}
function Assert-DevGameStopped {
    param([string]$Profile)
    if ($Profile -eq 'dev' -and @(Get-Process -Name ck3 -ErrorAction SilentlyContinue).Count) { throw 'Close CK3 before replacing development output.' }
}
function Build-Aspirations {
    param([string]$RepositoryRoot, [ValidateSet('dev','release')][string]$Profile)
    $root = Get-RepositoryRoot $RepositoryRoot
    Assert-DevGameStopped $Profile
    $paths = Get-GeneratedPaths $root $Profile
    $assembly = Get-AssemblyEntries $root $Profile
    [IO.Directory]::CreateDirectory($paths.Build) | Out-Null
    $stage = Assert-ContainedPath (Join-Path $paths.Build ('.stage-' + [Guid]::NewGuid().ToString('N'))) $paths.Build
    $stageMod = Join-Path $stage 'mod'
    $backup = $null
    try {
        [IO.Directory]::CreateDirectory($stageMod) | Out-Null
        foreach ($entry in $assembly.Entries) {
            $destination = Assert-ContainedPath (Join-Path $stageMod $entry.Destination) $stageMod
            if ($entry.Destination -eq 'descriptor.mod') { Write-Utf8Text $destination $assembly.Descriptor.Text }
            else {
                [IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($destination)) | Out-Null
                [IO.File]::Copy((Join-Path $root $entry.Source), $destination)
                if ((Get-ContentHash $destination) -ne $entry.Hash) { throw "Source changed during assembly: $($entry.Source)" }
            }
            $entry.Hash = Get-ContentHash $destination
        }
        Test-NativeContent $stageMod $Profile $assembly.Descriptor
        $manifestText = ConvertTo-Json -InputObject @($assembly.Entries) -Depth 4
        Write-Utf8Text (Join-Path $stage 'manifest.json') ($manifestText.Replace("`r`n", "`n") + "`n")
        # Recheck immediately before replacement; replacement owns mod/ only.
        Assert-DevGameStopped $Profile
        $paths = Get-GeneratedPaths $root $Profile
        [IO.Directory]::CreateDirectory($paths.Profile) | Out-Null
        if ([IO.Directory]::Exists($paths.Mod)) {
            $backup = Assert-ContainedPath (Join-Path $paths.Build ('.previous-' + [Guid]::NewGuid().ToString('N'))) $paths.Build
            [IO.Directory]::Move($paths.Mod, $backup)
        }
        try {
            [IO.Directory]::Move($stageMod, $paths.Mod)
            [IO.File]::Move((Join-Path $stage 'manifest.json'), $paths.Manifest, $true)
        } catch {
            if ([IO.Directory]::Exists($paths.Mod)) { Remove-Item -LiteralPath $paths.Mod -Recurse -Force }
            if ($backup) { [IO.Directory]::Move($backup, $paths.Mod); $backup = $null }
            throw
        }
        if ($backup) { Assert-NoReparsePath $backup; @(Get-SafeFiles $backup) | Out-Null; Remove-Item -LiteralPath $backup -Recurse -Force; $backup = $null }
    } finally {
        if ([IO.Directory]::Exists($stage)) { Assert-ContainedPath $stage $paths.Build | Out-Null; @(Get-SafeFiles $stage) | Out-Null; Remove-Item -LiteralPath $stage -Recurse -Force }
    }
    Write-Host "Verified mod root: $($paths.Mod)"
    Write-Host "Manifest: $($paths.Manifest)"
    Write-Host 'Static assembly checks only; CK3 runtime semantics and gameplay are unverified.'
    return $paths.Mod
}
function Test-Aspirations {
    param([string]$RepositoryRoot, [ValidateSet('dev','release')][string]$Profile)
    $root = Get-RepositoryRoot $RepositoryRoot
    $assembly = Get-AssemblyEntries $root $Profile
    $paths = Get-GeneratedPaths $root $Profile
    if (-not [IO.Directory]::Exists($paths.Mod) -or -not [IO.File]::Exists($paths.Manifest)) { throw 'Build this profile before checking output.' }
    Test-NativeContent $paths.Mod $Profile $assembly.Descriptor
    $manifest = @(ConvertFrom-Json -InputObject ([IO.File]::ReadAllText($paths.Manifest)))
    $outputFiles = @(Get-SafeFiles $paths.Mod)
    if ($manifest.Count -ne $assembly.Entries.Count -or $manifest.Count -ne $outputFiles.Count) { throw 'Source, output and manifest file counts differ.' }
    for ($i = 0; $i -lt $manifest.Count; $i++) {
        $actual = $manifest[$i]
        $expected = $assembly.Entries[$i]
        if ($actual.Source -cne $expected.Source -or $actual.Destination -cne $expected.Destination) { throw 'Manifest does not match ordered source entries.' }
        Assert-RelativePath $actual.Source
        Assert-RelativePath $actual.Destination
        $outputPath = Assert-ContainedPath (Join-Path $paths.Mod $actual.Destination) $paths.Mod
        if (-not [IO.File]::Exists($outputPath) -or $actual.Hash -cne (Get-ContentHash $outputPath)) { throw "Output hash mismatch: $($actual.Destination)" }
        if ($expected.Hash -and $actual.Hash -cne $expected.Hash) { throw "Source changed since build: $($actual.Source)" }
    }
    Write-Host "Static checks passed: $Profile ($($manifest.Count) files)."
    Write-Host 'Limitations: focused definition/encoding/layout checks cannot prove CK3 script semantics, knowledge, attribution, timings, UI, or gameplay.'
}
function Install-AspirationsDev {
    param([string]$RepositoryRoot, [string]$UserDataPath)
    $root = Get-RepositoryRoot $RepositoryRoot
    $userData = [IO.Path]::GetFullPath($UserDataPath)
    Assert-NoReparsePath $userData
    if (-not [IO.Directory]::Exists($userData)) { throw 'UserDataPath must be an existing, explicitly selected CK3 user-data directory.' }
    $modDirectory = Assert-ContainedPath (Join-Path $userData 'mod') $userData
    $registration = Assert-ContainedPath (Join-Path $modDirectory 'aspirations_dev.mod') $userData
    Assert-NoReparsePath $registration
    $mod = Build-Aspirations $root dev
    Test-Aspirations $root dev
    $descriptor = Get-Descriptor $root dev
    $portablePath = $mod.Replace('\', '/')
    if ($portablePath -match '["\r\n]') { throw 'Unsupported characters in local registration path.' }
    Write-Utf8Text $registration ($descriptor.Text + 'path="' + $portablePath + '"' + "`n")
    Write-Host "Registered development descriptor: $registration"
    Write-Host 'Select Aspirations (Development) in your disposable playset separately.'
}
function New-AspirationsPackage {
    param([string]$RepositoryRoot)
    $root = Get-RepositoryRoot $RepositoryRoot
    $dist = Assert-ContainedPath (Join-Path $root 'dist') $root
    Assert-NoReparsePath $dist
    $descriptor = Get-Descriptor $root release
    $zipPath = Assert-ContainedPath (Join-Path $dist "aspirations-$($descriptor.Version).zip") $dist
    Assert-NoReparsePath $zipPath
    $mod = Build-Aspirations $root release
    Test-Aspirations $root release
    [IO.Directory]::CreateDirectory($dist) | Out-Null
    $temporary = Assert-ContainedPath (Join-Path $dist ('.package-' + [Guid]::NewGuid().ToString('N') + '.zip')) $dist
    $stream = [IO.File]::Open($temporary, [IO.FileMode]::CreateNew)
    $archive = [IO.Compression.ZipArchive]::new($stream, [IO.Compression.ZipArchiveMode]::Create, $false)
    try {
        $files = [Collections.Generic.List[object]]::new()
        foreach ($path in @(Get-SafeFiles $mod)) { $files.Add([pscustomobject]@{ Name = 'mod/' + (Get-RelativeName $mod $path); Path = $path }) }
        foreach ($name in @('INSTALL.md','CREDITS.md')) { $files.Add([pscustomobject]@{ Name = $name; Path = Join-Path $root "packaging/$name" }) }
        foreach ($file in @($files | Sort-Object -Property Name -CaseSensitive -Culture '')) {
            $entry = $archive.CreateEntry($file.Name, [IO.Compression.CompressionLevel]::Optimal)
            $entry.LastWriteTime = [DateTimeOffset]::new(2000,1,1,0,0,0,[TimeSpan]::Zero)
            $input = [IO.File]::OpenRead($file.Path)
            $output = $entry.Open()
            try { $input.CopyTo($output) } finally { $output.Dispose(); $input.Dispose() }
        }
    } finally { $archive.Dispose(); $stream.Dispose() }
    Assert-NoReparsePath $zipPath
    [IO.File]::Move($temporary, $zipPath, $true)
    Write-Host "Release archive: $zipPath"
}
Export-ModuleMember -Function Build-Aspirations, Test-Aspirations, Install-AspirationsDev, New-AspirationsPackage
