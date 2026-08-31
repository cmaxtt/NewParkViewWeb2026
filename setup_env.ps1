<#
.SYNOPSIS
    One-time credential setup for Park View Drugs on THIS server.
    Generates a fresh random SECRET_KEY and prompts for the admin
    password, then stores both as MACHINE-level environment variables
    (required because the scheduled task runs as SYSTEM).

.DESCRIPTION
    Run as Administrator once per server, BEFORE install_service.ps1.
    The app reads these at startup:
      PARKVIEW_SECRET_KEY        - session signing key (random 64 hex)
      PARKVIEW_ADMIN_PASSWORD_HASH - werkzeug scrypt hash of your admin password
#>
$ErrorActionPreference = 'Stop'

$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: Please run as Administrator (right-click > Run as Administrator)" -ForegroundColor Red
    pause
    exit 1
}

Write-Host "=== Park View Drugs - Credential Setup ===" -ForegroundColor Green

# 1. Secret key (random)
$secret = [System.Convert]::ToHexString([System.Security.Cryptography.RandomNumberGenerator]::GetBytes(32)).ToLower()
[Environment]::SetEnvironmentVariable('PARKVIEW_SECRET_KEY', $secret, 'Machine')
Write-Host "[OK] PARKVIEW_SECRET_KEY generated and stored (Machine)." -ForegroundColor Green

# 2. Admin password hash
$python = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path $python)) {
    Write-Host "ERROR: $python not found. Create the virtual environment and install requirements first." -ForegroundColor Red
    pause
    exit 1
}

$pw = Read-Host "Enter the admin panel password (min 8 chars)"
if ($pw.Length -lt 8) {
    Write-Host "ERROR: password too short (min 8 characters)." -ForegroundColor Red
    pause
    exit 1
}
$confirm = Read-Host "Confirm password"
if ($pw -ne $confirm) {
    Write-Host "ERROR: passwords do not match." -ForegroundColor Red
    pause
    exit 1
}

$hash = & $python -c "from werkzeug.security import generate_password_hash; import sys; print(generate_password_hash(sys.argv[1]))" $pw
if ($LASTEXITCODE -ne 0 -or -not $hash) {
    Write-Host "ERROR: could not generate password hash." -ForegroundColor Red
    pause
    exit 1
}
[Environment]::SetEnvironmentVariable('PARKVIEW_ADMIN_PASSWORD_HASH', $hash.Trim(), 'Machine')
Write-Host "[OK] PARKVIEW_ADMIN_PASSWORD_HASH generated and stored (Machine)." -ForegroundColor Green

Write-Host ""
Write-Host "=== Done ===" -ForegroundColor Green
Write-Host "Machine env vars set: PARKVIEW_SECRET_KEY, PARKVIEW_ADMIN_PASSWORD_HASH"
Write-Host "Next step: run install_service.ps1 as Administrator to register the scheduled task."
Write-Host ""
pause
