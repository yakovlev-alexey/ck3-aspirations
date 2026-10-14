[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidateSet('dev','release')][string]$Profile,
    [Parameter(Mandatory)][string]$GamePath,
    [string]$TigerPath,
    [switch]$FailOnWarning,
    [ValidateRange(1,900)][int]$TimeoutSeconds = 300,
    [string]$RepositoryRoot = (Join-Path $PSScriptRoot '..')
)
$ErrorActionPreference = 'Stop'
try {
    Import-Module (Join-Path $PSScriptRoot 'Aspirations.XTiger.psm1') -Force
    $result = Test-AspirationsXTiger -RepositoryRoot $RepositoryRoot -Profile $Profile -GamePath $GamePath -TigerPath $TigerPath -FailOnWarning:$FailOnWarning -TimeoutSeconds $TimeoutSeconds
    if (-not $result.Passed) { exit 1 }
    exit 0
} catch { Write-Error $_ -ErrorAction Continue; exit 1 }
