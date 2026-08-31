<#
.SYNOPSIS
    Daily Park View Drugs database backup. Copies instance\parkview.db to
    backup\parkview-<timestamp>.db and keeps the newest 14 copies.
    Registered as the 'ParkViewDrugsBackup' scheduled task by install_service.ps1.
#>
$ErrorActionPreference = 'Stop'

$db = Join-Path $PSScriptRoot 'instance\parkview.db'
$bakDir = Join-Path $PSScriptRoot 'backup'

if (-not (Test-Path $db)) {
    Write-Host "[Backup] No database found at $db - nothing to back up."
    exit 0
}

New-Item -ItemType Directory -Force -Path $bakDir | Out-Null
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$target = Join-Path $bakDir "parkview-$stamp.db"

Copy-Item $db $target -Force
Write-Host "[Backup] Copied $db -> $target"

# Retention: keep the newest 14
Get-ChildItem $bakDir -Filter 'parkview-*.db' |
    Sort-Object LastWriteTime -Descending |
    Select-Object -Skip 14 |
    Remove-Item -Force -ErrorAction SilentlyContinue
Write-Host "[Backup] Retention applied (14 kept)."
