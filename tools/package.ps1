[CmdletBinding()]
param([string]$RepositoryRoot = (Join-Path $PSScriptRoot '..'))
$ErrorActionPreference = 'Stop'
try {
    Import-Module (Join-Path $PSScriptRoot 'Aspirations.Build.psm1') -Force
    New-AspirationsPackage -RepositoryRoot $RepositoryRoot
    exit 0
} catch { Write-Error $_ -ErrorAction Continue; exit 1 }
