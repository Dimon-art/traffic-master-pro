param(
    [Parameter(Mandatory=$true)]
    [string]$BackupFile
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $BackupFile)) {
    Write-Host "[ERROR] File not found: $BackupFile"
    exit 1
}

Write-Host "[WARNING] This will OVERWRITE all current data in the DB!"
Write-Host "Current DB will be replaced with: $BackupFile"
$confirm = Read-Host "Continue? (yes/no)"
if ($confirm -ne "yes") {
    Write-Host "Cancelled."
    exit 0
}

Get-Content $BackupFile -Raw | docker compose exec -T db psql -U trainer -d traffic_master

Write-Host "[OK] Backup restored from: $BackupFile"
