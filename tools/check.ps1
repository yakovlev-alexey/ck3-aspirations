[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidateSet('dev','release')][string]$Profile,
    [string]$RepositoryRoot = (Join-Path $PSScriptRoot '..')
)
$ErrorActionPreference = 'Stop'
try {
    Import-Module (Join-Path $PSScriptRoot 'Aspirations.Build.psm1') -Force
    & (Join-Path $PSScriptRoot 'check-contracts.ps1') -RepositoryRoot $RepositoryRoot
    if ($LASTEXITCODE -ne 0) { throw 'Shared story source contracts failed' }
    Test-Aspirations -RepositoryRoot $RepositoryRoot -Profile $Profile
    exit 0
} catch { Write-Error $_ -ErrorAction Continue; exit 1 }
