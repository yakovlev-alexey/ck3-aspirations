[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidateNotNullOrEmpty()][string]$UserDataPath,
    [string]$RepositoryRoot = (Join-Path $PSScriptRoot '..')
)
$ErrorActionPreference = 'Stop'
try {
    Import-Module (Join-Path $PSScriptRoot 'Aspirations.Build.psm1') -Force
    Install-AspirationsDev -RepositoryRoot $RepositoryRoot -UserDataPath $UserDataPath
    exit 0
} catch { Write-Error $_ -ErrorAction Continue; exit 1 }
