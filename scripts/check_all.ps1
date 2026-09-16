# Runs backend pytest (docker) and frontend vitest (host).

$ErrorActionPreference = "Continue"

Write-Host "[CHECK] Backend tests (docker)..."
docker compose exec -T backend pytest -q
$backendExit = $LASTEXITCODE

Write-Host "[CHECK] Frontend tests (host)..."
Push-Location frontend
npm test -- --run
$frontendExit = $LASTEXITCODE
Pop-Location

Write-Host ""
if ($backendExit -eq 0 -and $frontendExit -eq 0) {
    Write-Host "[OK] All checks passed"
    exit 0
} else {
    Write-Host "[FAIL] Some checks failed"
    Write-Host "  backend exit code: $backendExit"
    Write-Host "  frontend exit code: $frontendExit"
    exit 1
}
