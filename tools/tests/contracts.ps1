# Shared acceptance/source contract boundaries; no CK3 engine execution.
param([string]$RepositoryRoot = (Join-Path $PSScriptRoot '../..'))
$ErrorActionPreference = 'Stop'
$repo = [IO.Path]::GetFullPath($RepositoryRoot)
$checker = Join-Path $repo 'tools/check-contracts.ps1'
if (-not (Test-Path -LiteralPath $checker)) { throw 'Shared story contract checker is missing' }
$pwsh = (Get-Process -Id $PID).Path
$testRoot = Join-Path $repo ('.local/contract-tests/' + [Guid]::NewGuid().ToString('N'))
$utf8 = [Text.UTF8Encoding]::new($false)
$failures = [Collections.Generic.List[string]]::new()
function Write-Text($Path, $Text) {
    [IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($Path)) | Out-Null
    [IO.File]::WriteAllText($Path, $Text, $utf8)
}
function Assert($Condition, $Message) { if (-not $Condition) { throw $Message } }
function New-Fixture($Name) {
    $root = Join-Path $testRoot $Name
    $rows = @()
    foreach ($family in @('vengeance','holding_recovery','personal_bond')) {
        $scenario = @{ vengeance = 'vengeance-regression'; holding_recovery = 'recovery-regression'; personal_bond = 'bond-regression' }[$family]
        Write-Text (Join-Path $root "src/stories/$family/SPEC.md") "# Family`n[Acceptance](tests/scenarios.md)"
        Write-Text (Join-Path $root "src/stories/$family/tests/scenarios.md") "# Scenarios`n| F01 | Exact target | Once |`nRegistered ``$scenario``."
        Write-Text (Join-Path $root "src/stories/$family/tests/game/events/asp_fixture.txt") 'asp_test_fixture.1 = {}'
        Write-Text (Join-Path $root "src/stories/$family/game/common/story_cycles/asp_story.txt") "asp_${family}_story = { visible = yes visualization = { custom_string_key = `"asp_${family}_body`" } }`nasp_${family}_context_story = { visible = no }"
        Write-Text (Join-Path $root "src/stories/$family/game/localization/english/asp_fixture_l_english.yml") "l_english:`n asp_${family}_story:0 `"Title`"`n asp_${family}_story_desc:0 `"Description`"`n asp_${family}_body:0 `"[Story.MakeScope.Var('asp_target').Char.GetShortUIName]``nPrivate``nAge/review`""
        $case = "[``F01``](../src/stories/$family/tests/scenarios.md)"
        $rows += "| ``$family`` | $case | $case | $case | $case | $case | ``$scenario`` [Fixture](../src/stories/$family/tests/game/events/asp_fixture.txt) |"
    }
    Write-Text (Join-Path $root 'docs/story-authoring.md') ("# Story guide`n## Current family evidence`n| Family | Origin and target | Lifecycle | Completion and cancellation | Stale actions | Presentation | Registered regression |`n| --- | --- | --- | --- | --- | --- | --- |`n" + ($rows -join "`n") + "`n## New family template`nProse owns behavior.")
    Write-Text (Join-Path $root 'docs/knowledge/README.md') '# Knowledge index'
    Write-Text (Join-Path $root 'tools/game_runner/scenarios.json') '["vengeance-regression", "recovery-regression", "bond-regression"]'
    return $root
}
function Check($Root, $ExpectedError = '') {
    $output = & $pwsh -NoProfile -File $checker -RepositoryRoot $Root 2>&1
    $code = $LASTEXITCODE
    if ($ExpectedError) {
        Assert ($code -ne 0) 'Invalid contract fixture passed'
        Assert (($output -join "`n") -match $ExpectedError) "Wrong rejection: $($output -join ' ')"
    } else { Assert ($code -eq 0) "Valid fixture rejected: $($output -join ' ')" }
}
function Case($Name, $Body) {
    try { & $Body; Write-Host "$Name PASS" }
    catch { $failures.Add("$Name FAIL: $($_.Exception.Message)"); Write-Host $failures[-1] }
}
Case 'K01 visible stories and invisible contexts' { Check (New-Fixture K01) }
Case 'K02 missing family evidence' {
    $root = New-Fixture K02
    $path = Join-Path $root 'docs/story-authoring.md'
    Write-Text $path ([IO.File]::ReadAllText($path) -replace '(?m)^\| `personal_bond`.*\r?\n', '')
    Check $root 'Missing acceptance evidence row.*personal_bond'
}
Case 'K03 missing acceptance category' {
    $root = New-Fixture K03
    $path = Join-Path $root 'docs/story-authoring.md'
    $text = [IO.File]::ReadAllText($path)
    $text = $text.Replace('| `vengeance` | [`F01`](../src/stories/vengeance/tests/scenarios.md) |', '| `vengeance` | |')
    Write-Text $path $text
    Check $root 'Missing Origin and target evidence.*vengeance'
}
Case 'K04 stale scenario reference' {
    $root = New-Fixture K04
    $path = Join-Path $root 'docs/story-authoring.md'
    Write-Text $path ([IO.File]::ReadAllText($path).Replace('[`F01`](../src/stories/vengeance/tests/scenarios.md)', '[`F99`](../src/stories/vengeance/tests/scenarios.md)'))
    Check $root 'Unknown acceptance scenario.*F99'
}
Case 'K05 unregistered regression' {
    $root = New-Fixture K05
    $path = Join-Path $root 'tools/game_runner/scenarios.json'
    Write-Text $path '["recovery-regression", "bond-regression"]'
    Check $root 'Unregistered regression.*vengeance-regression'
}
Case 'K06 missing native fixture' {
    $root = New-Fixture K06
    Remove-Item -LiteralPath (Join-Path $root 'src/stories/vengeance/tests/game/events/asp_fixture.txt')
    Check $root 'Broken documentation link'
}
Case 'K07 native implicit and visualization keys' {
    foreach ($key in @('asp_vengeance_story','asp_vengeance_story_desc','asp_vengeance_body')) {
        $root = New-Fixture $key
        $path = Join-Path $root 'src/stories/vengeance/game/localization/english/asp_fixture_l_english.yml'
        Write-Text $path ([IO.File]::ReadAllText($path) -replace "(?m)^ $($key):.*\r?\n?", '')
        Check $root "Missing visible Story localization.*$key"
    }
}
Case 'K08 comments and quoted braces do not invent visible stories' {
    $root = New-Fixture K08
    $path = Join-Path $root 'src/stories/vengeance/game/common/story_cycles/asp_story.txt'
    Add-Content -LiteralPath $path '# asp_phantom_story = { visible = yes }'
    Add-Content -LiteralPath $path 'asp_invisible = { visible = no text = "} visible = yes {" }'
    Check $root
}
Case 'K09 future family requires evidence and accepts documented coverage' {
    $root = New-Fixture K09
    Write-Text (Join-Path $root 'src/stories/future_story/SPEC.md') "# Future`n[Acceptance](tests/scenarios.md)"
    Write-Text (Join-Path $root 'src/stories/future_story/tests/scenarios.md') "| N01 | Fixed target | Once |`nRegistered ``future-regression``."
    Write-Text (Join-Path $root 'src/stories/future_story/tests/game/events/asp_future.txt') 'asp_test_future.1 = {}'
    Check $root 'Missing acceptance evidence row.*future_story'
    $case = '[`N01`](../src/stories/future_story/tests/scenarios.md)'
    $path = Join-Path $root 'docs/story-authoring.md'
    Write-Text $path ([IO.File]::ReadAllText($path).Replace('## New family template', "| ``future_story`` | $case | $case | $case | $case | $case | ``future-regression`` [Fixture](../src/stories/future_story/tests/game/events/asp_future.txt) |`n## New family template"))
    Write-Text (Join-Path $root 'tools/game_runner/scenarios.json') '["vengeance-regression", "recovery-regression", "bond-regression", "future-regression"]'
    Check $root
}
Case 'K10 knowledge evidence cannot depend only on ignored local reports' {
    $root = New-Fixture K10
    Write-Text (Join-Path $root '.local/report.md') '# Ignored report'
    Write-Text (Join-Path $root 'docs/knowledge/automation.md') '[Evidence](../../.local/report.md)'
    Check $root 'Nonportable knowledge evidence'
}
Case 'K11 broken knowledge navigation' {
    $root = New-Fixture K11
    Write-Text (Join-Path $root 'docs/knowledge/README.md') '[Payer](missing.md)'
    Check $root 'Broken documentation link'
}
Case 'K12 literal template links are not repository navigation' {
    $root = New-Fixture K12
    $path = Join-Path $root 'docs/story-authoring.md'
    Add-Content -LiteralPath $path ("`n" + '```markdown' + "`n" + '[Example](../../core/SPEC.md)' + "`n" + '```')
    Check $root
}
Case 'K13 another family cannot supply origin or terminal evidence' {
    $root = New-Fixture K13
    $path = Join-Path $root 'docs/story-authoring.md'
    Write-Text $path ([IO.File]::ReadAllText($path).Replace('[`F01`](../src/stories/vengeance/tests/scenarios.md)', '[`F01`](../src/stories/personal_bond/tests/scenarios.md)'))
    Check $root 'Acceptance evidence belongs to another family'
}
Case 'K14 another family fixture cannot satisfy registered evidence' {
    $root = New-Fixture K14
    $path = Join-Path $root 'docs/story-authoring.md'
    Write-Text $path ([IO.File]::ReadAllText($path).Replace('[Fixture](../src/stories/vengeance/tests/game/events/asp_fixture.txt)', '[Fixture](../src/stories/personal_bond/tests/game/events/asp_fixture.txt)'))
    Check $root 'Regression fixture must be dev-only native source'
}
Case 'K15 nested native cards retain implicit key checks' {
    $root = New-Fixture K15
    foreach ($part in @('common/story_cycles','localization/english')) {
        $directory = Join-Path $root "src/stories/vengeance/game/$part"
        [IO.Directory]::CreateDirectory((Join-Path $directory 'nested')) | Out-Null
        foreach ($file in Get-ChildItem -LiteralPath $directory -File) {
            # Both endpoints are explicit descendants of this disposable fixture.
            Move-Item -LiteralPath $file.FullName -Destination (Join-Path (Join-Path $directory 'nested') $file.Name)
        }
    }
    Check $root
    $path = Join-Path $root 'src/stories/vengeance/game/localization/english/nested/asp_fixture_l_english.yml'
    Write-Text $path ([IO.File]::ReadAllText($path) -replace '(?m)^ asp_vengeance_story_desc:.*\r?\n?', '')
    Check $root 'Missing visible Story localization.*asp_vengeance_story_desc'
}
Write-Host "Contract fixtures: $testRoot"
if ($failures.Count) { Write-Host "$($failures.Count) contract cases failed"; exit 1 }
Write-Host 'All 15 shared contract cases passed'; exit 0
