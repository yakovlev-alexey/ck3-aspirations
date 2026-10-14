Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$script:Utf8 = [Text.UTF8Encoding]::new($false, $true)

function Get-XTigerRelease {
    ConvertFrom-Json -InputObject ([IO.File]::ReadAllText((Join-Path $PSScriptRoot 'xtiger/release.json'), $script:Utf8))
}
function Get-XTigerLocalPath {
    param([string]$RepositoryRoot, [string]$Relative)
    $root = [IO.Path]::GetFullPath($RepositoryRoot)
    if (-not [IO.Directory]::Exists($root)) { throw 'Repository root must already exist.' }
    $localRoot = Join-Path $root '.local'
    $path = [IO.Path]::GetFullPath((Join-Path $localRoot $Relative))
    if (-not $path.StartsWith($localRoot + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) { throw 'xTiger output must stay under repository .local/.' }
    $cursor = $path
    while ($cursor) {
        if ((Test-Path -LiteralPath $cursor) -and ((Get-Item -LiteralPath $cursor -Force).Attributes -band [IO.FileAttributes]::ReparsePoint)) { throw "xTiger output traverses a reparse point: $cursor" }
        $cursor = [IO.Path]::GetDirectoryName($cursor)
    }
    return $path
}
function Expand-XTigerArchive {
    param([string]$RepositoryRoot, [string]$ArchivePath, [string]$Destination, [string]$ExpectedHash)
    if ((Get-FileHash -LiteralPath $ArchivePath -Algorithm SHA256).Hash -ine $ExpectedHash) { throw 'xTiger archive SHA-256 mismatch; executable was not extracted.' }
    $localRoot = Join-Path ([IO.Path]::GetFullPath($RepositoryRoot)) '.local'
    $relative = [IO.Path]::GetRelativePath($localRoot, [IO.Path]::GetFullPath($Destination))
    $destinationRoot = Get-XTigerLocalPath $RepositoryRoot $relative
    $archive = [IO.Compression.ZipFile]::OpenRead($ArchivePath)
    try {
        $executableEntry = (Get-XTigerRelease).ExecutableEntry
        $executables = @()
        foreach ($entry in $archive.Entries) {
            $name = $entry.FullName.Replace('\', '/')
            if ($name -match '^/|:|(^|/)\.\.(/|$)') { throw 'Unsafe path in xTiger archive.' }
            if ($name -ceq $executableEntry) { $executables += $entry }
        }
        if ($executables.Count -ne 1) { throw "xTiger archive must contain exactly one $executableEntry." }
        [IO.Directory]::CreateDirectory($destinationRoot) | Out-Null
        $output = Get-XTigerLocalPath $RepositoryRoot (Join-Path $relative 'ck3-tiger.exe')
        [IO.Compression.ZipFileExtensions]::ExtractToFile($executables[0], $output, $true)
        return $output
    } finally { $archive.Dispose() }
}
function Install-AspirationsXTiger {
    param([string]$RepositoryRoot, [string]$ArchivePath)
    if (-not $IsWindows) { throw 'The pinned xTiger package is for Windows.' }
    $release = Get-XTigerRelease
    $directory = Get-XTigerLocalPath $RepositoryRoot "tools/xtiger/$($release.Version)"
    if (-not $ArchivePath) {
        [IO.Directory]::CreateDirectory($directory) | Out-Null
        $ArchivePath = Get-XTigerLocalPath $RepositoryRoot "tools/xtiger/$($release.Version)/archive.zip"
        if (-not [IO.File]::Exists($ArchivePath)) {
            $download = Get-XTigerLocalPath $RepositoryRoot "tools/xtiger/$($release.Version)/download-$([Guid]::NewGuid().ToString('N')).zip"
            try {
                Invoke-WebRequest -Uri $release.Url -OutFile $download
                if ((Get-FileHash -LiteralPath $download -Algorithm SHA256).Hash -ine $release.Sha256) { throw 'xTiger download SHA-256 mismatch.' }
                [IO.File]::Move($download, $ArchivePath)
            } finally { if ([IO.File]::Exists($download)) { [IO.File]::Delete($download) } }
        }
    }
    $executable = Expand-XTigerArchive $RepositoryRoot $ArchivePath (Join-Path $directory 'bin') $release.Sha256
    Write-Host "Installed xTiger $($release.Version): $executable"
}
function Invoke-XTigerProcess {
    param([string]$Executable, [string[]]$Arguments, [int]$TimeoutSeconds)
    $start = [Diagnostics.ProcessStartInfo]::new()
    $start.FileName = $Executable
    $start.UseShellExecute = $false
    $start.CreateNoWindow = $true
    $start.RedirectStandardOutput = $true
    $start.RedirectStandardError = $true
    $start.StandardOutputEncoding = $script:Utf8
    $start.StandardErrorEncoding = $script:Utf8
    foreach ($argument in $Arguments) { $start.ArgumentList.Add($argument) }
    $process = [Diagnostics.Process]::new()
    $process.StartInfo = $start
    try {
        if (-not $process.Start()) { throw 'Could not start xTiger.' }
        $stdout = $process.StandardOutput.ReadToEndAsync()
        $stderr = $process.StandardError.ReadToEndAsync()
        if (-not $process.WaitForExit($TimeoutSeconds * 1000)) {
            $process.Kill($true)
            $process.WaitForExit()
            throw "xTiger exceeded the $TimeoutSeconds second timeout."
        }
        return [pscustomobject]@{ Stdout = $stdout.GetAwaiter().GetResult(); Stderr = $stderr.GetAwaiter().GetResult(); ExitCode = $process.ExitCode }
    } finally { $process.Dispose() }
}
function Test-AspirationsXTiger {
    param(
        [string]$RepositoryRoot,
        [ValidateSet('dev','release')][string]$Profile,
        [string]$GamePath,
        [string]$TigerPath,
        [string]$ConfigPath = (Join-Path $PSScriptRoot 'xtiger/ck3-tiger.conf'),
        [switch]$FailOnWarning,
        [ValidateRange(1,900)][int]$TimeoutSeconds = 300
    )
    $root = [IO.Path]::GetFullPath($RepositoryRoot)
    # Preserve the existing source-contract and exact source/output/hash preflight.
    & (Join-Path $PSScriptRoot 'check.ps1') -RepositoryRoot $root -Profile $Profile
    if ($LASTEXITCODE -ne 0) { throw 'Build/check preflight failed; xTiger was not run.' }
    $release = Get-XTigerRelease
    if (-not $TigerPath) { $TigerPath = Get-XTigerLocalPath $root "tools/xtiger/$($release.Version)/bin/ck3-tiger.exe" }
    if (-not [IO.File]::Exists($TigerPath)) { throw 'xTiger is missing. Run tools/setup-xtiger.ps1 first, or supply -TigerPath.' }
    $TigerPath = [IO.Path]::GetFullPath($TigerPath)
    $GamePath = [IO.Path]::GetFullPath($GamePath)
    $ConfigPath = [IO.Path]::GetFullPath($ConfigPath)
    if (-not [IO.File]::Exists((Join-Path $GamePath 'game/events/witch_events.txt'))) { throw '-GamePath must be the CK3 installation root containing game/ and launcher/.' }
    if (-not [IO.File]::Exists($ConfigPath)) { throw 'Missing xTiger configuration.' }
    $validatorHash = (Get-FileHash -LiteralPath $TigerPath).Hash.ToLowerInvariant()
    $configHash = (Get-FileHash -LiteralPath $ConfigPath).Hash.ToLowerInvariant()
    $version = Invoke-XTigerProcess $TigerPath @('--version') 15
    if ($version.ExitCode -ne 0 -or $version.Stdout.Trim() -cne "ck3-tiger $($release.Version)") { throw "Expected xTiger $($release.Version); run tools/setup-xtiger.ps1. Upstream Tiger is not supported here." }
    $directory = Get-XTigerLocalPath $root "xtiger/$Profile/$([Guid]::NewGuid().ToString('N'))"
    [IO.Directory]::CreateDirectory($directory) | Out-Null
    $descriptor = Join-Path $root ".build/$Profile/mod/descriptor.mod"
    $manifest = Join-Path $root ".build/$Profile/manifest.json"
    $manifestHash = (Get-FileHash -LiteralPath $manifest).Hash.ToLowerInvariant()
    $native = Invoke-XTigerProcess $TigerPath @('--json','--no-color','--game',$GamePath,'--config',$ConfigPath,$descriptor) $TimeoutSeconds
    $reportPath = Join-Path $directory 'reports.json'
    [IO.File]::WriteAllText($reportPath, $native.Stdout, $script:Utf8)
    [IO.File]::WriteAllText((Join-Path $directory 'stderr.txt'), $native.Stderr, $script:Utf8)
    if ($native.ExitCode -ne 0) { throw "xTiger exited $($native.ExitCode). Evidence: $directory" }
    if ([string]::IsNullOrWhiteSpace($native.Stdout)) { throw "xTiger returned no JSON. Evidence: $directory" }
    $reports = ConvertFrom-Json -InputObject $native.Stdout -AsHashtable -NoEnumerate
    if ($reports -isnot [array]) { throw "xTiger report must be a JSON array. Evidence: $directory" }
    $counts = [ordered]@{ fatal = 0; error = 0; warning = 0; untidy = 0; tips = 0 }
    foreach ($report in $reports) {
        if ($report -isnot [Collections.IDictionary] -or $report.severity -isnot [string] -or -not $counts.Contains($report.severity) -or $report.key -isnot [string] -or $report.message -isnot [string] -or $report.locations -isnot [array]) { throw "Malformed xTiger diagnostic. Evidence: $directory" }
        $counts[$report.severity]++
    }
    # A validation must remain tied to the same source/output, even during a long run.
    & (Join-Path $PSScriptRoot 'check.ps1') -RepositoryRoot $root -Profile $Profile
    if ($LASTEXITCODE -ne 0 -or (Get-FileHash -LiteralPath $manifest).Hash -ine $manifestHash) { throw "Build changed during xTiger validation. Evidence: $directory" }
    if ((Get-FileHash -LiteralPath $TigerPath).Hash -ine $validatorHash -or (Get-FileHash -LiteralPath $ConfigPath).Hash -ine $configHash) { throw "Validator/config changed during xTiger validation. Evidence: $directory" }
    $passed = $counts.fatal -eq 0 -and $counts.error -eq 0 -and (-not $FailOnWarning -or $counts.warning -eq 0)
    $gameVersion = 'unknown'
    $launcher = Join-Path $GamePath 'launcher/launcher-settings.json'
    if ([IO.File]::Exists($launcher)) { $gameVersion = (ConvertFrom-Json -InputObject ([IO.File]::ReadAllText($launcher, $script:Utf8))).version }
    $summaryPath = Join-Path $directory 'summary.json'
    $summary = [ordered]@{
        ValidatorRepository = $release.Repository; ValidatorVersion = $release.Version
        ValidatorHash = $validatorHash
        ConfigHash = $configHash
        GameVersion = $gameVersion; Profile = $Profile; ManifestHash = $manifestHash
        FailOnWarning = [bool]$FailOnWarning; NativeExitCode = $native.ExitCode
        Counts = $counts; Passed = $passed
    }
    [IO.File]::WriteAllText($summaryPath, (($summary | ConvertTo-Json -Depth 6) + "`n"), $script:Utf8)
    Write-Host "xTiger $($release.Version): fatal=$($counts.fatal), error=$($counts.error), warning=$($counts.warning), untidy=$($counts.untidy), tips=$($counts.tips)"
    Write-Host "JSON reports: $reportPath"
    return [pscustomobject]@{ Passed = $passed; Counts = $counts; ReportPath = $reportPath; SummaryPath = $summaryPath }
}
Export-ModuleMember -Function Install-AspirationsXTiger, Test-AspirationsXTiger
