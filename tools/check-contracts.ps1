[CmdletBinding()]
param([string]$RepositoryRoot = (Join-Path $PSScriptRoot '..'))
$ErrorActionPreference = 'Stop'
# This is a source documentation/key check, not a CK3 parser or semantic oracle.
function Read-TrackedText([string]$Relative) {
    $path = [IO.Path]::GetFullPath((Join-Path $script:Root $Relative))
    if (-not $path.StartsWith($script:Root + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) { throw "Documentation path escapes repository: $Relative" }
    $cursor = $path
    while ($cursor -and $cursor.StartsWith($script:Root, [StringComparison]::OrdinalIgnoreCase)) {
        if ((Test-Path -LiteralPath $cursor) -and ((Get-Item -LiteralPath $cursor -Force).Attributes -band [IO.FileAttributes]::ReparsePoint)) { throw "Contract reference traverses a reparse point: $Relative" }
        $cursor = [IO.Path]::GetDirectoryName($cursor)
    }
    if (-not [IO.File]::Exists($path)) { throw "Missing contract file: $Relative" }
    return [IO.File]::ReadAllText($path)
}
function Resolve-Reference([string]$Document, [string]$Link) {
    $target = $Link.Split('#')[0]
    if (-not $target -or $target -match '^[a-zA-Z][a-zA-Z0-9+.-]*:') { return $null }
    $relative = [IO.Path]::GetRelativePath($script:Root, [IO.Path]::GetFullPath((Join-Path (Join-Path $script:Root ([IO.Path]::GetDirectoryName($Document))) $target))).Replace('\', '/')
    if ($relative -match '^(?:\.local|\.build|\.superpowers|dist)/') { throw "Nonportable knowledge evidence in ${Document}: $Link" }
    try { $null = Read-TrackedText $relative } catch { throw "Broken documentation link in ${Document}: $Link ($($_.Exception.Message))" }
    return $relative
}
function Test-References([string]$Document) {
    $prose = [regex]::Replace((Read-TrackedText $Document), '(?ms)^```[^\n]*\n.*?^```[^\n]*', '')
    foreach ($link in [regex]::Matches($prose, '\]\(([^)]+)\)')) { $null = Resolve-Reference $Document $link.Groups[1].Value }
}
function Test-FamilyEvidence {
    $guide = Read-TrackedText 'docs/story-authoring.md'
    $table = [regex]::Match($guide, '(?ms)^## Current family evidence\s*\n(.*?)(?=^## |\z)').Groups[1].Value
    $rows = @{}
    foreach ($line in $table -split '\r?\n') {
        if ($line -notmatch '^\|\s*`([a-z][a-z0-9_]*)`\s*\|') { continue }
        $family = $Matches[1]
        if ($rows.ContainsKey($family)) { throw "Duplicate acceptance evidence row: $family" }
        $cells = @($line.Trim().Trim('|').Split('|') | ForEach-Object { $_.Trim() })
        if ($cells.Count -ne 7) { throw "Acceptance evidence row needs all six coverage columns: $family" }
        $rows[$family] = $cells
    }
    $registry = @(ConvertFrom-Json (Read-TrackedText 'tools/game_runner/scenarios.json'))
    if (-not $registry.Count -or @($registry | Where-Object { $_ -isnot [string] -or $_ -notmatch '^[a-z][a-z0-9-]+$' }).Count -or @($registry | Select-Object -Unique).Count -ne $registry.Count) { throw 'Invalid shared runner scenario registry' }
    $families = @(Get-ChildItem -LiteralPath (Join-Path $script:Root 'src/stories') -Directory | ForEach-Object { $_.Name })
    foreach ($family in $families) {
        $spec = Read-TrackedText "src/stories/$family/SPEC.md"
        if ($spec -notmatch '\]\(tests/scenarios\.md(?:#[^)]+)?\)') { throw "Family SPEC must link its acceptance scenarios: $family" }
        $scenarios = Read-TrackedText "src/stories/$family/tests/scenarios.md"
        if (-not $rows.ContainsKey($family)) { throw "Missing acceptance evidence row: $family" }
        $cells = $rows[$family]
        $categories = @('Origin and target','Lifecycle','Completion and cancellation','Stale actions','Presentation')
        for ($index = 0; $index -lt $categories.Count; $index++) {
            $hasFamilyEvidence = $false
            $references = [regex]::Matches($cells[$index + 1], '\[`([A-Z][0-9]{2})`\]\(([^)]+)\)')
            if (-not $references.Count) { throw "Missing $($categories[$index]) evidence: $family" }
            foreach ($reference in $references) {
                $case = $reference.Groups[1].Value
                $document = Resolve-Reference 'docs/story-authoring.md' $reference.Groups[2].Value
                if (-not $document -or $document -notmatch '/tests/scenarios\.md$') { throw "Acceptance evidence must link a module scenario: $family/$case" }
                if ($document -cne "src/core/tests/scenarios.md" -and $document -cne "src/stories/$family/tests/scenarios.md") { throw "Acceptance evidence belongs to another family: $family/$document" }
                if ($document -ceq "src/stories/$family/tests/scenarios.md") { $hasFamilyEvidence = $true }
                if ((Read-TrackedText $document) -notmatch "(?m)^\|\s*$case\s*\|") { throw "Unknown acceptance scenario: $family/$case in $document" }
            }
            if ($index -in @(0, 2) -and -not $hasFamilyEvidence) { throw "Missing owning family $($categories[$index]) evidence: $family" }
        }
        $registered = [regex]::Match($cells[6], '`([a-z][a-z0-9-]+)`').Groups[1].Value
        if (-not $registered -or $registered -cnotin $registry) { throw "Unregistered regression: $family/$registered" }
        if ($scenarios -notmatch [regex]::Escape($registered)) { throw "Family scenarios must document registered regression: $family/$registered" }
        $fixtures = [regex]::Matches($cells[6], '\]\(([^)]+\.txt)\)')
        if (-not $fixtures.Count) { throw "Missing native regression fixture reference: $family" }
        foreach ($fixture in $fixtures) {
            $relative = Resolve-Reference 'docs/story-authoring.md' $fixture.Groups[1].Value
            if ($relative -notmatch "^src/(?:core|stories/$([regex]::Escape($family)))/tests/game/") { throw "Regression fixture must be dev-only native source: $family/$relative" }
        }
        Test-References "src/stories/$family/SPEC.md"
        Test-References "src/stories/$family/tests/scenarios.md"
    }
    foreach ($family in $rows.Keys) { if ($family -cnotin $families) { throw "Unknown acceptance family: $family" } }
    Test-References 'docs/story-authoring.md'
}
function Test-StoryKeys {
    foreach ($family in Get-ChildItem -LiteralPath (Join-Path $script:Root 'src/stories') -Directory) {
        $storyRoot = Join-Path $family.FullName 'game/common/story_cycles'
        if (-not (Test-Path -LiteralPath $storyRoot)) { continue }
        $keys = [Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
        $localizationRoot = Join-Path $family.FullName 'game/localization/english'
        if (Test-Path -LiteralPath $localizationRoot) {
            foreach ($file in Get-ChildItem -LiteralPath $localizationRoot -Recurse -File -Filter '*.yml') {
                $text = Read-TrackedText ([IO.Path]::GetRelativePath($script:Root, $file.FullName))
                foreach ($key in [regex]::Matches($text, '(?m)^\s*(asp_[a-zA-Z0-9_]+):[0-9]*\s+"')) { $null = $keys.Add($key.Groups[1].Value) }
            }
        }
        foreach ($file in Get-ChildItem -LiteralPath $storyRoot -Recurse -File -Filter '*.txt') {
            $source = Read-TrackedText ([IO.Path]::GetRelativePath($script:Root, $file.FullName))
            # Mask quoted strings/comments before counting braces or matching visibility.
            $masked = [regex]::Replace($source, '"(?:\\.|[^"\\])*"|#[^\r\n]*', [Text.RegularExpressions.MatchEvaluator]{ param($match) return [regex]::Replace($match.Value, '[^\r\n]', ' ') })
            foreach ($definition in [regex]::Matches($masked, '(?m)^\s*(asp_[a-zA-Z0-9_]+)\s*=\s*\{')) {
                $start = $definition.Index + $definition.Length
                $depth = 1; $end = $start
                while ($end -lt $masked.Length -and $depth) {
                    if ($masked[$end] -eq '{') { $depth++ }
                    if ($masked[$end] -eq '}') { $depth-- }
                    $end++
                }
                if ($depth) { throw "Unclosed Story definition: $($definition.Groups[1].Value)" }
                $body = $masked.Substring($start, $end - $start - 1)
                if ($body -notmatch '\bvisible\s*=\s*yes\b') { continue }
                $story = $definition.Groups[1].Value
                $requiredKeys = @($story, ($story + '_desc'))
                $visualization = [regex]::Match($body, '\bcustom_string_key\s*=')
                if (-not $visualization.Success) { throw "Visible Story needs explicit state visualization: $story" }
                $value = $source.Substring($start + $visualization.Index + $visualization.Length)
                $key = [regex]::Match($value, '^\s*"?(asp_[a-zA-Z0-9_]+)"?').Groups[1].Value
                if (-not $key) { throw "Visible Story needs a static visualization key: $story" }
                $requiredKeys += $key
                foreach ($required in $requiredKeys) { if (-not $keys.Contains($required)) { throw "Missing visible Story localization: $story/$required" } }
            }
        }
    }
}
try {
    $script:Root = [IO.Path]::GetFullPath($RepositoryRoot).TrimEnd([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar)
    Test-FamilyEvidence
    Test-StoryKeys
    $null = Read-TrackedText 'docs/knowledge/README.md'
    foreach ($note in Get-ChildItem -LiteralPath (Join-Path $script:Root 'docs/knowledge') -File -Filter '*.md') { Test-References ([IO.Path]::GetRelativePath($script:Root, $note.FullName)) }
    Write-Host 'Shared story evidence references and native card keys passed (static checks only)'
    exit 0
} catch { Write-Error $_ -ErrorAction Continue; exit 1 }
