# Real command integration tests. Each case catches a boundary regression.
$ErrorActionPreference = 'Stop'
$repo = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$pwsh = (Get-Process -Id $PID).Path
$testRoot = Join-Path $repo ('.local/tool-tests/' + [Guid]::NewGuid().ToString('N'))
[IO.Directory]::CreateDirectory($testRoot) | Out-Null
$utf8 = [Text.UTF8Encoding]::new($false)
$failures = [Collections.Generic.List[string]]::new()
function Write-Text($Path, $Text) {
    [IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($Path)) | Out-Null
    [IO.File]::WriteAllText($Path, $Text, $utf8)
}
function Assert($Condition, $Message) { if (-not $Condition) { throw $Message } }
function New-Fixture($Name) {
    $root = Join-Path $testRoot $Name
    [IO.Directory]::CreateDirectory($root) | Out-Null
    foreach ($path in @('docs/design.md','docs/repository.md','docs/modding-notes.md','README.md','AGENTS.md','packaging/INSTALL.md','packaging/CREDITS.md')) { Write-Text (Join-Path $root $path) '# Fixture' }
    foreach ($module in @('core','stories/vengeance','stories/holding_recovery','stories/personal_bond')) {
        Write-Text (Join-Path $root "src/$module/SPEC.md") "# Fixture`n[Acceptance](tests/scenarios.md)"
        Write-Text (Join-Path $root "src/$module/tests/scenarios.md") '# Fixture scenarios'
    }
    Write-Text (Join-Path $root 'packaging/descriptor.mod') "name=`"Aspirations`"`nversion=`"0.1.0`"`nsupported_version=`"1.20.*`"`ntags={ `"Gameplay`" }`n"
    $rows = @()
    foreach ($family in @('vengeance','holding_recovery','personal_bond')) {
        $scenario = @{ vengeance = 'vengeance-regression'; holding_recovery = 'recovery-regression'; personal_bond = 'bond-regression' }[$family]
        Write-Text (Join-Path $root "src/stories/$family/tests/scenarios.md") "# Fixture scenarios`n| F01 | Exact target | Once |`nRegistered ``$scenario``."
        Write-Text (Join-Path $root "src/stories/$family/tests/game/events/asp_${family}_contract_fixture.txt") "asp_test_${family}_contract.1 = {}"
        $case = "[``F01``](../src/stories/$family/tests/scenarios.md)"
        $rows += "| ``$family`` | $case | $case | $case | $case | $case | ``$scenario`` [Fixture](../src/stories/$family/tests/game/events/asp_${family}_contract_fixture.txt) |"
    }
    Write-Text (Join-Path $root 'docs/story-authoring.md') ("# Fixture guide`n## Current family evidence`n" + ($rows -join "`n") + "`n## New family template`n")
    Write-Text (Join-Path $root 'docs/knowledge/README.md') '# Fixture knowledge'
    Write-Text (Join-Path $root 'tools/game_runner/scenarios.json') '["vengeance-regression", "recovery-regression", "bond-regression"]'
    return $root
}
function Run-Tool($Name, $Root, $Extra = @(), $ExpectFailure = $false) {
    $script = Join-Path $repo "tools/$Name.ps1"
    Assert (Test-Path -LiteralPath $script) "Missing assembly/check command: tools/$Name.ps1"
    $output = & $pwsh -NoProfile -File $script -RepositoryRoot $Root @Extra 2>&1
    $code = $LASTEXITCODE
    if ($ExpectFailure) { Assert ($code -ne 0) "$Name accepted invalid fixture" }
    else { Assert ($code -eq 0) "$Name failed ($code): $($output -join ' ')" }
    return ($output -join "`n")
}
function Case($Id, $Body) {
    try { & $Body; Write-Host "$Id PASS" }
    catch { $failures.Add("$Id FAIL: $($_.Exception.Message)"); Write-Host $failures[-1] }
}
try {
    Case 'T01 byte/path preservation and deterministic manifests' {
        $root = New-Fixture 'T01 space path'
        $script = Join-Path $root 'src/stories/vengeance/game/events/nested path/asp_vengeance_events.txt'
        Write-Text $script "namespace = asp_vengeance`nasp_vengeance.1 = { type = character_event }`r`n"
        $loc = Join-Path $root 'src/stories/vengeance/game/localization/english/asp_vengeance_l_english.yml'
        [IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($loc)) | Out-Null
        [IO.File]::WriteAllText($loc, "l_english:`r`n asp_vengeance_title:0 `"A loved one`"`r`n", [Text.UTF8Encoding]::new($true))
        Run-Tool build $root @('-Profile','dev') | Out-Null
        foreach ($pair in @(@($script,'events/nested path/asp_vengeance_events.txt'), @($loc,'localization/english/asp_vengeance_l_english.yml'))) {
            Assert ((Get-FileHash -LiteralPath $pair[0]).Hash -eq (Get-FileHash -LiteralPath (Join-Path $root ".build/dev/mod/$($pair[1])")).Hash) 'T01: source bytes changed'
        }
        $manifest = [IO.File]::ReadAllText((Join-Path $root '.build/dev/manifest.json'))
        Assert (-not $manifest.Contains($root)) 'T01: machine path leaked'
        Run-Tool build $root @('-Profile','dev') | Out-Null
        Assert ($manifest -ceq [IO.File]::ReadAllText((Join-Path $root '.build/dev/manifest.json'))) 'T01: manifest is nondeterministic'
        Run-Tool check $root @('-Profile','dev') | Out-Null
    }
    Case 'T02 exact and case-only collision rejection' {
        foreach ($name in @('asp_shared.txt','ASP_SHARED.txt')) {
            $root = New-Fixture ('T02-' + [Guid]::NewGuid().ToString('N'))
            Write-Text (Join-Path $root 'src/core/game/common/scripted_effects/asp_shared.txt') 'asp_shared_effect = {}'
            Write-Text (Join-Path $root "src/stories/vengeance/game/common/scripted_effects/$name") 'asp_other_effect = {}'
            Run-Tool build $root @('-Profile','dev') $true | Out-Null
            Assert (-not (Test-Path -LiteralPath (Join-Path $root '.build/dev/mod'))) 'T02: collision produced output'
        }
    }
    Case 'T03 stale cleanup and sentinel preservation' {
        $root = New-Fixture T03
        $source = Join-Path $root 'src/core/game/events/asp_old.txt'
        Write-Text $source 'asp_core.1 = {}'
        Run-Tool build $root @('-Profile','dev') | Out-Null
        $sentinel = Join-Path $root '.build/dev/unrelated.txt'
        Write-Text $sentinel 'keep me'
        Remove-Item -LiteralPath $source
        Run-Tool build $root @('-Profile','dev') | Out-Null
        Assert (-not (Test-Path -LiteralPath (Join-Path $root '.build/dev/mod/events/asp_old.txt'))) 'T03: stale file retained'
        Assert (Test-Path -LiteralPath $sentinel) 'T03: unrelated file removed'
    }
    Case 'T04 dev fixture exclusion and descriptor separation' {
        $root = New-Fixture T04
        Write-Text (Join-Path $root 'src/core/tests/game/events/asp_core_debug_events.txt') 'asp_test_core.1 = {}'
        Run-Tool build $root @('-Profile','dev') | Out-Null
        Run-Tool build $root @('-Profile','release') | Out-Null
        Assert (Test-Path -LiteralPath (Join-Path $root '.build/dev/mod/events/asp_core_debug_events.txt')) 'T04: dev fixture missing'
        Assert (-not (Test-Path -LiteralPath (Join-Path $root '.build/release/mod/events/asp_core_debug_events.txt'))) 'T04: debug fixture leaked'
        Assert ([IO.File]::ReadAllText((Join-Path $root '.build/dev/mod/descriptor.mod')).Contains('Aspirations (Development)')) 'T04: dev title missing'
    }
    Case 'T05 output and source reparse escape rejection' {
        $outside = Join-Path $testRoot 'outside'
        Write-Text (Join-Path $outside 'sentinel.txt') 'untouched'
        $root = New-Fixture T05output
        [IO.Directory]::CreateDirectory((Join-Path $root '.build')) | Out-Null
        New-Item -ItemType Junction -Path (Join-Path $root '.build/dev') -Target $outside | Out-Null
        Run-Tool build $root @('-Profile','dev') $true | Out-Null
        Assert ([IO.File]::ReadAllText((Join-Path $outside 'sentinel.txt')) -eq 'untouched') 'T05: output escape modified outside data'
        $root = New-Fixture T05source
        [IO.Directory]::CreateDirectory((Join-Path $root 'src/core/game')) | Out-Null
        New-Item -ItemType Junction -Path (Join-Path $root 'src/core/game/events') -Target $outside | Out-Null
        Run-Tool build $root @('-Profile','dev') $true | Out-Null
        $root = New-Fixture T05preview
        Add-Content -LiteralPath (Join-Path $root 'packaging/descriptor.mod') 'picture="../outside/sentinel.txt"'
        Run-Tool build $root @('-Profile','release') $true | Out-Null
    }
    Case 'T06 staging failure retains last good output' {
        $root = New-Fixture T06
        Write-Text (Join-Path $root 'src/core/game/events/asp_core_events.txt') 'asp_core.1 = {}'
        Run-Tool build $root @('-Profile','dev') | Out-Null
        $before = (Get-FileHash -LiteralPath (Join-Path $root '.build/dev/mod/events/asp_core_events.txt')).Hash
        Write-Text (Join-Path $root 'src/core/game/localization/english/asp_bad_l_english.yml') "l_english:`n asp_bad:0 `"Missing BOM`""
        Run-Tool build $root @('-Profile','dev') $true | Out-Null
        Assert ($before -eq (Get-FileHash -LiteralPath (Join-Path $root '.build/dev/mod/events/asp_core_events.txt')).Hash) 'T06: previous output changed'
    }
    Case 'T07 static content and descriptor validation' {
        foreach ($bad in @('duplicate','foreign-language','broken-link','placeholder','absolute-path','debug-runtime')) {
            $root = New-Fixture "T07-$bad"
            switch ($bad) {
                duplicate {
                    Write-Text (Join-Path $root 'src/core/game/common/scripted_effects/asp_a.txt') 'asp_same_effect = {}'
                    Write-Text (Join-Path $root 'src/stories/vengeance/game/common/scripted_effects/asp_b.txt') 'asp_same_effect = {}'
                }
                foreign-language { Write-Text (Join-Path $root 'src/core/game/localization/french/asp_bad_l_french.yml') 'l_french:' }
                broken-link { Write-Text (Join-Path $root 'src/stories/vengeance/SPEC.md') '[Acceptance](tests/missing.md)' }
                placeholder { Add-Content -LiteralPath (Join-Path $root 'packaging/descriptor.mod') 'remote_file_id="1234567890"' }
                absolute-path { Add-Content -LiteralPath (Join-Path $root 'packaging/descriptor.mod') 'path="C:/example/mod"' }
                debug-runtime { Write-Text (Join-Path $root 'src/core/game/events/asp_debug.txt') 'asp_test_core.1 = {}' }
            }
            Run-Tool build $root @('-Profile','release') $true | Out-Null
        }
        $root = New-Fixture T07tamper
        Run-Tool build $root @('-Profile','release') | Out-Null
        Write-Text (Join-Path $root '.build/release/mod/rogue.md') 'not native content'
        Run-Tool check $root @('-Profile','release') $true | Out-Null
    }
    Case 'T08 explicit registration and deterministic archive' {
        $root = New-Fixture T08
        Add-Content -LiteralPath (Join-Path $root 'packaging/descriptor.mod') 'remote_file_id="3487654321"'
        $userData = Join-Path $testRoot 'disposable user data'
        Write-Text (Join-Path $userData 'mod/unrelated.mod') 'preserve'
        Run-Tool install-dev $root @('-UserDataPath',$userData) | Out-Null
        $descriptor = [IO.File]::ReadAllText((Join-Path $userData 'mod/aspirations_dev.mod'))
        Assert ($descriptor.Contains('Aspirations (Development)')) 'T08: wrong registration name'
        Assert (-not $descriptor.Contains('remote_file_id')) 'T08: release ID leaked into dev'
        Assert ([IO.File]::ReadAllText((Join-Path $userData 'mod/unrelated.mod')) -eq 'preserve') 'T08: unrelated registration changed'
        Run-Tool package $root | Out-Null
        $zip = Join-Path $root 'dist/aspirations-0.1.0.zip'
        $hash = (Get-FileHash -LiteralPath $zip).Hash
        $archive = [IO.Compression.ZipFile]::OpenRead($zip)
        try {
            Assert ($null -ne $archive.GetEntry('mod/descriptor.mod')) 'T08: archive mod root missing'
            Assert ($null -ne $archive.GetEntry('INSTALL.md')) 'T08: install instructions missing'
            Assert ($null -ne $archive.GetEntry('CREDITS.md')) 'T08: credits missing'
            $reader = [IO.StreamReader]::new($archive.GetEntry('mod/descriptor.mod').Open())
            try { Assert ($reader.ReadToEnd().Contains('3487654321')) 'T08: real release ID lost' } finally { $reader.Dispose() }
        } finally { $archive.Dispose() }
        Run-Tool package $root | Out-Null
        Assert ($hash -eq (Get-FileHash -LiteralPath $zip).Hash) 'T08: archive nondeterministic'
        Run-Tool install-dev $root @('-UserDataPath',(Join-Path $testRoot 'missing-user-data')) $true | Out-Null
    }
    Case 'T09 duplicate scalar ID rejection' {
        $root = New-Fixture T09scalar
        Write-Text (Join-Path $root 'src/core/game/common/script_values/asp_a.txt') 'asp_same_value = 5'
        Write-Text (Join-Path $root 'src/stories/vengeance/game/common/script_values/asp_b.txt') 'asp_same_value = 10'
        Run-Tool build $root @('-Profile','release') $true | Out-Null
    }
    Case 'T10 descriptor key allowlist' {
        $root = New-Fixture T10metadata
        Add-Content -LiteralPath (Join-Path $root 'packaging/descriptor.mod') 'unexpected_path="C:/private/location"'
        Run-Tool build $root @('-Profile','release') $true | Out-Null
    }
    # R1 catches metadata hidden after a valid-looking tags block, and incomplete grammar.
    $descriptorCases = [ordered]@{
        'T11 inline path' = 'tags={ "Gameplay" } path="D:/example/local-mod"'
        'T12 inline archive' = 'tags={ "Gameplay" } archive="local.zip"'
        'T13 inline unknown field' = 'tags={ "Gameplay" } unexpected_path="D:/example/local-mod"'
        'T14 inline duplicate scalar field' = 'tags={ "Gameplay" } version="9.9.9"'
        'T15 duplicate tags field' = 'tags={ "Gameplay" } tags={ "Events" }'
        'T16 unclosed tags block' = 'tags={ "Gameplay"'
        'T17 unparsed trailing text' = 'tags={ "Gameplay" } stray text'
        'T18 malformed tags value' = 'tags={ "Gameplay" unquoted }'
    }
    foreach ($caseName in $descriptorCases.Keys) {
        Case $caseName {
            $root = New-Fixture ($caseName.Replace(' ', '-'))
            $descriptor = Join-Path $root 'packaging/descriptor.mod'
            $content = [IO.File]::ReadAllText($descriptor).Replace('tags={ "Gameplay" }', $descriptorCases[$caseName])
            Write-Text $descriptor $content
            Run-Tool build $root @('-Profile','release') $true | Out-Null
        }
    }
    Case 'T19 misplaced debug localization rejected in release and usable in dev' {
        $root = New-Fixture T19
        $loc = Join-Path $root 'src/core/game/localization/english/asp_core_l_english.yml'
        [IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($loc)) | Out-Null
        [IO.File]::WriteAllText($loc, "l_english:`n asp_test_core_label:0 `"Debug only`"`n", [Text.UTF8Encoding]::new($true))
        Run-Tool build $root @('-Profile','dev') | Out-Null
        Run-Tool check $root @('-Profile','dev') | Out-Null
        Run-Tool build $root @('-Profile','release') $true | Out-Null
    }
    Case 'T20 additional language header rejected' {
        $root = New-Fixture T20
        $loc = Join-Path $root 'src/core/game/localization/english/asp_core_l_english.yml'
        [IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($loc)) | Out-Null
        [IO.File]::WriteAllText($loc, "l_english:`n asp_core_label:0 `"English`"`nl_french:`n asp_core_other:0 `"French`"`n", [Text.UTF8Encoding]::new($true))
        Run-Tool build $root @('-Profile','release') $true | Out-Null
        Run-Tool build $root @('-Profile','dev') $true | Out-Null
    }
    Case 'T21 multiline tags and inline scalar metadata remain valid' {
        $root = New-Fixture T21
        $descriptor = Join-Path $root 'packaging/descriptor.mod'
        Write-Text $descriptor "name=`"Aspirations`" version=`"0.1.0`"`nsupported_version=`"1.20.*`"`ntags={`n # ordinary multiline list`n `"Gameplay`"`n `"Events`"`n}`nremote_file_id=`"3487654321`"`n"
        Run-Tool build $root @('-Profile','release') | Out-Null
        Run-Tool check $root @('-Profile','release') | Out-Null
        Run-Tool build $root @('-Profile','dev') | Out-Null
        Run-Tool check $root @('-Profile','dev') | Out-Null
        $dev = [IO.File]::ReadAllText((Join-Path $root '.build/dev/mod/descriptor.mod'))
        Assert ($dev.Contains('version="0.1.0"')) 'T21: inline metadata lost in dev'
        Assert ($dev.Contains('Aspirations (Development)')) 'T21: dev name missing'
        Assert (-not $dev.Contains('remote_file_id')) 'T21: Workshop ID leaked to dev'
    }
    Case 'T22 escaped closing quote cannot hide an unterminated tag' {
        $root = New-Fixture T22
        $descriptor = Join-Path $root 'packaging/descriptor.mod'
        $content = [IO.File]::ReadAllText($descriptor).Replace('tags={ "Gameplay" }', 'tags={ "Gameplay\" }')
        Write-Text $descriptor $content
        Run-Tool build $root @('-Profile','release') $true | Out-Null
    }
    Case 'T23 corrupted and duplicate script BOM rejection' {
        $badPrefixes = @(([string][char]0xEF + [char]0xBB + [char]0xBF), ([string][char]0xFEFF + [char]0xFEFF))
        foreach ($prefix in $badPrefixes) {
            $root = New-Fixture ('T23-' + [Guid]::NewGuid().ToString('N'))
            Write-Text (Join-Path $root 'src/core/game/events/asp_core_events.txt') ($prefix + 'asp_core.1 = {}')
            $output = Run-Tool build $root @('-Profile','release') $true
            Assert ($output -match 'Invalid UTF-8 BOM prefix') 'T23: failed for a reason other than the malformed prefix'
        }
    }
    Case 'T24 live exited and unverifiable CK3 rebuild guards' {
        $module = Import-Module (Join-Path $repo 'tools/Aspirations.Build.psm1') -Force -PassThru
        & $module {
            function script:Get-Process { [CmdletBinding()] param([string]$Name) return $script:aspGuardProbe }
            try {
                $script:aspGuardProbe = [pscustomobject]@{ HasExited = $false }
                $rejected = $false
                try { Assert-DevGameStopped dev } catch { $rejected = $true }
                if (-not $rejected) { throw 'T24: a live CK3 process did not block dev output' }
                $script:aspGuardProbe = [pscustomobject]@{ HasExited = $true }
                Assert-DevGameStopped dev
                $script:aspGuardProbe = [pscustomobject]@{ Name = 'ck3' }
                $rejected = $false
                try { Assert-DevGameStopped dev } catch { $rejected = $true }
                if (-not $rejected) { throw 'T24: unverifiable liveness did not fail closed' }
                $script:aspGuardProbe = @()
                Assert-DevGameStopped dev
            } finally { Remove-Item Function:script:Get-Process; Remove-Variable aspGuardProbe -Scope Script }
        }
    }
} finally {
    # Never recursively remove a linked fixture. Leave disposable roots ignored for inspection.
    Write-Host "Fixtures: $testRoot"
}
if ($failures.Count) { Write-Host "$($failures.Count) test cases failed"; exit 1 }
& $pwsh -NoProfile -File (Join-Path $PSScriptRoot 'contracts.ps1') -RepositoryRoot $repo
if ($LASTEXITCODE -ne 0) { exit 1 }
Write-Host 'All 24 tooling and 15 shared contract cases passed'; exit 0
