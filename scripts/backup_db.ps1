$ErrorActionPreference = "Stop"
$containerName = "traffic-master-pro-trainer-db-1"
$dbUser = "trainer"
$dbName = "traffic_master"
$backupDir = "backups"
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$backupFile = Join-Path $backupDir "backup_$timestamp.sql"
$running = docker ps --filter "name=$containerName" --format "{{.Names}}"
if (-not $running) { Write-Host "[ERROR] DB container is not running"; exit 1 }
if (-not (Test-Path $backupDir)) { New-Item -ItemType Directory -Path $backupDir | Out-Null }
Write-Host "[INFO] Creating backup..."
docker compose exec -T db pg_dump -U $dbUser $dbName | Out-File -Encoding utf8 $backupFile
$size = (Get-Item $backupFile).Length
Write-Host "[OK] Backup created: $backupFile"
Write-Host "     Size: $([math]::Round($size/1KB,2)) KB"
$cutoff = (Get-Date).AddDays(-30)
Get-ChildItem $backupDir -Filter "backup_*.sql" | Where-Object { $_.LastWriteTime -lt $cutoff } | Remove-Item -Force
