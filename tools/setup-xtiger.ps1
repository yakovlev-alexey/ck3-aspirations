[CmdletBinding()]
param(
    [string]$RepositoryRoot = (Join-Path $PSScriptRoot '..'),
    [string]$ArchivePath
)
$ErrorActionPreference = 'Stop'
try {
    Import-Module (Join-Path $PSScriptRoot 'Aspirations.XTiger.psm1') -Force
    Install-AspirationsXTiger -RepositoryRoot $RepositoryRoot -ArchivePath $ArchivePath
    exit 0
} catch { Write-Error $_ -ErrorAction Continue; exit 1 }
