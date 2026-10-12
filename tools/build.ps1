[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidateSet('dev','release')][string]$Profile,
    [string]$RepositoryRoot = (Join-Path $PSScriptRoot '..')
)
$ErrorActionPreference = 'Stop'
try {
    Import-Module (Join-Path $PSScriptRoot 'Aspirations.Build.psm1') -Force
    Build-Aspirations -RepositoryRoot $RepositoryRoot -Profile $Profile | Out-Null
    exit 0
} catch { Write-Error $_ -ErrorAction Continue; exit 1 }
