# Called by run.ps1; exercise our boundary, not xTiger's validation engine.
Case 'X01 xTiger integration is available' {
    Assert (Test-Path -LiteralPath (Join-Path $repo 'tools/Aspirations.XTiger.psm1')) 'Missing xTiger integration module'
    Import-Module (Join-Path $repo 'tools/Aspirations.XTiger.psm1') -Force
}
if (-not (Get-Module Aspirations.XTiger)) { return }
$xtigerModule = Get-Module Aspirations.XTiger
$xtigerRoot = New-Fixture 'XTiger space path'
Write-Text (Join-Path $xtigerRoot 'src/core/game/events/asp_probe.txt') 'namespace = asp_probe'
Run-Tool build $xtigerRoot @('-Profile','dev') | Out-Null
Run-Tool build $xtigerRoot @('-Profile','release') | Out-Null
$xtigerGame = Join-Path $testRoot 'XTiger game space'
Write-Text (Join-Path $xtigerGame 'game/events/witch_events.txt') '# Signature'
Write-Text (Join-Path $xtigerGame 'launcher/launcher-settings.json') '{"version":"1.20.1 (Crozier)"}'
$xtigerExecutable = Join-Path $testRoot 'xtiger.exe'
Write-Text $xtigerExecutable 'External process double; never executed.'
$xtigerConfig = Join-Path $testRoot 'xtiger.conf'
Write-Text $xtigerConfig 'languages = { check = "english" }'
# Only the external executable is replaced. Output, provenance and policy stay real.
& $xtigerModule {
    $script:ProcessFixture = [pscustomobject]@{ Json = '[]'; ExitCode = 0; Calls = @(); MutationPath = '' }
    function script:Invoke-XTigerProcess {
        param($Executable, $Arguments, $TimeoutSeconds)
        $script:ProcessFixture.Calls += ,@($Arguments)
        if ($Arguments[0] -eq '--version') {
            return [pscustomobject]@{ Stdout = 'ck3-tiger 1.5.9-alpha'; Stderr = ''; ExitCode = 0 }
        }
        if ($script:ProcessFixture.MutationPath) { [IO.File]::AppendAllText($script:ProcessFixture.MutationPath, "`n# changed during validation") }
        return [pscustomobject]@{ Stdout = $script:ProcessFixture.Json; Stderr = 'Fixture stderr'; ExitCode = $script:ProcessFixture.ExitCode }
    }
}
function Run-XTigerFixture($Json, $Code = 0, $FailOnWarning = $false, $Profile = 'dev', $MutationPath = '') {
    & $xtigerModule { param($Json, $Code, $MutationPath) $script:ProcessFixture.Json = $Json; $script:ProcessFixture.ExitCode = $Code; $script:ProcessFixture.Calls = @(); $script:ProcessFixture.MutationPath = $MutationPath } $Json $Code $MutationPath
    $arguments = @{ RepositoryRoot = $xtigerRoot; Profile = $Profile; GamePath = $xtigerGame; TigerPath = $xtigerExecutable; ConfigPath = $xtigerConfig; FailOnWarning = $FailOnWarning }
    Test-AspirationsXTiger @arguments
}
function New-XTigerDiagnostic($Severity) {
    return '[{"severity":"' + $Severity + '","confidence":"strong","key":"scope","message":"Fixture diagnostic","info":null,"wiki":null,"locations":[{"path":"events/asp_probe.txt","from":"mod","stage":null,"fullpath":"fixture","linenr":1,"column":1,"length":1,"line":"namespace = asp_probe","tag":null}]}]'
}
Case 'X02 empty reports and exact profile arguments' {
    foreach ($profile in @('dev','release')) {
        $result = Run-XTigerFixture '[]' 0 $false $profile
        Assert ($result.Passed -and $result.Counts.error -eq 0) 'Empty report rejected'
        $calls = & $xtigerModule { $script:ProcessFixture.Calls }
        $validation = $calls[-1]
        Assert ($validation -contains (Join-Path $xtigerRoot ".build/$profile/mod/descriptor.mod")) 'Wrong profile descriptor'
        Assert ($validation -contains $xtigerGame -and $validation -contains $xtigerConfig) 'Explicit paths not preserved'
        Assert ($validation -contains '--json' -and $validation -notcontains '--suppress') 'Reports suppressed or JSON omitted'
        Assert (Test-Path -LiteralPath $result.ReportPath) 'Raw JSON evidence missing'
        $summary = Get-Content -LiteralPath $result.SummaryPath -Raw | ConvertFrom-Json
        Assert ($summary.Profile -eq $profile -and $summary.ManifestHash -match '^[a-f0-9]{64}$') 'Missing build provenance'
        Assert ($summary.GameVersion -eq '1.20.1 (Crozier)') 'Installed game version not recorded'
    }
}
Case 'X03 diagnostic errors fail despite native exit zero' {
    foreach ($severity in @('error','fatal')) {
        $result = Run-XTigerFixture (New-XTigerDiagnostic $severity)
        Assert (-not $result.Passed) "Diagnostic $severity incorrectly passed"
        Assert ($result.Counts[$severity] -eq 1) 'Diagnostic not counted'
    }
}
Case 'X04 warning policy keeps advice nonblocking' {
    Assert ((Run-XTigerFixture (New-XTigerDiagnostic 'warning')).Passed) 'Warning failed default policy'
    Assert (-not (Run-XTigerFixture (New-XTigerDiagnostic 'warning') 0 $true).Passed) 'Strict policy ignored warning'
    foreach ($severity in @('tips','untidy')) { Assert ((Run-XTigerFixture (New-XTigerDiagnostic $severity) 0 $true).Passed) 'Advice incorrectly failed strict policy' }
}
Case 'X05 malformed reports fail closed' {
    foreach ($json in @('', 'not JSON', '{}', 'null', '[null]', '[{}]', '[{"severity":"unknown","message":"bad"}]')) {
        $rejected = $false
        try { Run-XTigerFixture $json | Out-Null } catch { $rejected = $true }
        Assert $rejected "Invalid xTiger report accepted: $json"
    }
}
Case 'X06 native failure is not an empty success' {
    $rejected = $false
    try { Run-XTigerFixture '[]' 7 | Out-Null } catch { $rejected = $true }
    Assert $rejected 'Nonzero validator exit accepted'
}
Case 'X07 stale build fails before external validation' {
    $path = Join-Path $xtigerRoot 'src/core/game/events/asp_probe.txt'
    Write-Text $path 'namespace = asp_changed'
    $rejected = $false
    try { Run-XTigerFixture '[]' | Out-Null } catch { $rejected = $true }
    Assert $rejected 'Stale output accepted'
    $calls = & $xtigerModule { $script:ProcessFixture.Calls }
    Assert ($calls.Count -eq 0) 'External validation ran on stale output'
    Write-Text $path 'namespace = asp_probe'
}
Case 'X08 archive digest and traversal checks precede extraction' {
    $archivePath = Join-Path $testRoot 'xtiger-test.zip'
    $stream = [IO.File]::Create($archivePath)
    $zip = [IO.Compression.ZipArchive]::new($stream, [IO.Compression.ZipArchiveMode]::Create)
    try {
        $entry = $zip.CreateEntry('../ck3-tiger.exe')
        $writer = [IO.StreamWriter]::new($entry.Open()); $writer.Write('bad'); $writer.Dispose()
    } finally { $zip.Dispose(); $stream.Dispose() }
    $destination = Join-Path $xtigerRoot '.local/tools/xtiger/probe'
    foreach ($digest in @(('0' * 64), (Get-FileHash -LiteralPath $archivePath).Hash)) {
        $rejected = $false
        try { & $xtigerModule { param($Root, $Archive, $Destination, $Hash) Expand-XTigerArchive $Root $Archive $Destination $Hash } $xtigerRoot $archivePath $destination $digest } catch { $rejected = $true }
        Assert $rejected 'Unsafe/unverified archive extracted'
        Assert (-not (Test-Path -LiteralPath (Join-Path $destination 'ck3-tiger.exe'))) 'Rejected archive wrote executable'
    }
    $validArchive = Join-Path $testRoot 'xtiger-valid.zip'
    $stream = [IO.File]::Create($validArchive)
    $zip = [IO.Compression.ZipArchive]::new($stream, [IO.Compression.ZipArchiveMode]::Create)
    try {
        foreach ($name in @('ck3-tiger.exe','xtiger-mcp.exe')) {
            $entry = $zip.CreateEntry("ck3-tiger-windows-v1.5.9-alpha/$name")
            $writer = [IO.StreamWriter]::new($entry.Open()); $writer.Write($name); $writer.Dispose()
        }
    } finally { $zip.Dispose(); $stream.Dispose() }
    $digest = (Get-FileHash -LiteralPath $validArchive).Hash
    $extracted = & $xtigerModule { param($Root, $Archive, $Destination, $Hash) Expand-XTigerArchive $Root $Archive $Destination $Hash } $xtigerRoot $validArchive $destination $digest
    Assert ([IO.File]::ReadAllText($extracted) -eq 'ck3-tiger.exe') 'Verified binary not extracted'
    Assert (-not (Test-Path -LiteralPath (Join-Path $destination 'xtiger-mcp.exe'))) 'Unused MCP executable installed'
}
Case 'X09 local report directory cannot follow a junction' {
    $outside = Join-Path $testRoot 'XTiger outside'
    [IO.Directory]::CreateDirectory($outside) | Out-Null
    $linkedRoot = New-Fixture 'XTiger linked root'
    New-Item -ItemType Junction -Path (Join-Path $linkedRoot '.local') -Target $outside | Out-Null
    $rejected = $false
    try { & $xtigerModule { param($Root) Get-XTigerLocalPath $Root 'xtiger' } $linkedRoot | Out-Null } catch { $rejected = $true }
    Assert $rejected 'Local output followed a junction'
    Assert (-not (Test-Path -LiteralPath (Join-Path $outside 'xtiger'))) 'External output was created'
}
Case 'X11 changed validator or configuration cannot claim input provenance' {
    foreach ($path in @($xtigerConfig, $xtigerExecutable)) {
        $before = [IO.File]::ReadAllBytes($path)
        $rejected = $false
        try { Run-XTigerFixture '[]' 0 $false 'dev' $path | Out-Null } catch { $rejected = $_.Exception.Message -match 'changed during' }
        finally { [IO.File]::WriteAllBytes($path, $before) }
        Assert $rejected 'Changed validator/config accepted as checked input'
    }
}
Remove-Module Aspirations.XTiger
Case 'X10 native output exit status and timeout ownership' {
    Import-Module (Join-Path $repo 'tools/Aspirations.XTiger.psm1') -Force
    $module = Get-Module Aspirations.XTiger
    $result = & $module { param($Pwsh) Invoke-XTigerProcess $Pwsh @('-NoProfile','-NonInteractive','-Command','[Console]::Out.Write("[]"); [Console]::Error.Write("native stderr"); exit 7') 10 } $pwsh
    Assert ($result.Stdout -eq '[]' -and $result.Stderr -eq 'native stderr' -and $result.ExitCode -eq 7) 'Native output/status corrupted'
    $rejected = $false
    try { & $module { param($Pwsh) Invoke-XTigerProcess $Pwsh @('-NoProfile','-NonInteractive','-Command','Start-Sleep -Seconds 10') 1 } $pwsh | Out-Null } catch { $rejected = $_.Exception.Message -match 'timeout' }
    Assert $rejected 'Native timeout was not enforced'
    Remove-Module Aspirations.XTiger
}
