<#
.SYNOPSIS
    Installs Park View Drugs Flask app as a persistent Windows scheduled task.
    The task auto-starts at system boot and runs whether any user is logged in.
.DESCRIPTION
    Run this once as Administrator to register the task.
    The app will be available at http://100.89.199.87:5000/ on Tailscale
    even when Hermes/terminal is closed.
#>

$TaskName = "ParkViewDrugsServer"

# Resolve the app directory from this script's own location (distributable).
$AppDir = $PSScriptRoot
if ([string]::IsNullOrEmpty($AppDir)) { $AppDir = "C:\aa-NewWeb" }
$TaskPath = Join-Path $AppDir "start_server.bat"
$WorkingDir = $AppDir
$LogFile = Join-Path $AppDir "install.log"

Start-Transcript -Path $LogFile -Append

Write-Host "=== Park View Drugs - Persistent Server Installer ===" -ForegroundColor Green

# Check if running as Admin
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: Please run as Administrator (right-click > Run as Administrator)" -ForegroundColor Red
    pause
    exit 1
}

# Check the controlled runtime exists
$AppDir = $PSScriptRoot
if ([string]::IsNullOrEmpty($AppDir)) { $AppDir = "C:\aa-NewWeb" }
$pythonPath = Join-Path $AppDir ".venv\Scripts\python.exe"
if (-not (Test-Path $pythonPath)) {
    Write-Host "ERROR: $pythonPath not found. Create the virtual environment and install requirements first." -ForegroundColor Red
    pause
    exit 1
}
Write-Host "[OK] Python found: $pythonPath" -ForegroundColor Green

# Ensure dependencies are installed (idempotent) and VERIFY before registering.
# This prevents the "No module named 'waitress'" failure mode.
Write-Host "[..] Ensuring dependencies are installed..." -ForegroundColor Cyan
& $pythonPath -m pip install --upgrade pip --quiet
& $pythonPath -m pip install -r (Join-Path $AppDir "requirements.txt") --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: pip install failed. See output above." -ForegroundColor Red
    pause
    exit 1
}
$importCheck = & $pythonPath -c "import flask, waitress; print('deps-ok')" 2>&1
if ($importCheck -ne 'deps-ok') {
    Write-Host "ERROR: dependency check failed: $importCheck" -ForegroundColor Red
    pause
    exit 1
}
Write-Host "[OK] Dependencies verified (flask + waitress)." -ForegroundColor Green

# Check app files exist
if (-not (Test-Path $TaskPath)) {
    Write-Host "ERROR: $TaskPath not found" -ForegroundColor Red
    pause
    exit 1
}
Write-Host "[OK] Startup script found" -ForegroundColor Green

# Remove existing task if present
$existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "Removing existing task..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# Create the scheduled task
$Action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$TaskPath`"" -WorkingDirectory $WorkingDir

# Trigger: at system startup
$Trigger = New-ScheduledTaskTrigger -AtStartup

# Run as the current user (with logon), or use SYSTEM
$Principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

# Settings: restart on failure; NO execution time limit (a server task must run forever)
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1) -ExecutionTimeLimit 0

# Register
Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Principal $Principal -Settings $Settings -Description "Park View Drugs Flask app (Waitress) - persistent server"

Write-Host ""
Write-Host "[OK] Task '$TaskName' installed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "  Started at boot?  Yes (SYSTEM account)"
Write-Host "  Auto-restart?     Yes (up to 3 times, 1-min interval)"
Write-Host "  Working dir:      $WorkingDir"
Write-Host "  Script:           $TaskPath"
Write-Host ""
Write-Host "Starting task now..." -ForegroundColor Cyan
Start-ScheduledTask -TaskName $TaskName

# Wait for the app to become healthy (up to 30 s) via the /healthz endpoint
Write-Host "[..] Waiting for the app to become healthy..." -ForegroundColor Cyan
$healthy = $false
for ($i = 0; $i -lt 30; $i++) {
    Start-Sleep -Seconds 1
    try {
        $h = Invoke-RestMethod -Uri 'http://127.0.0.1:5000/healthz' -TimeoutSec 3
        if ($h.status -eq 'ok') { $healthy = $true; break }
    } catch { }
}
if ($healthy) {
    Write-Host "[OK] App is healthy (HTTP 200 on /healthz)." -ForegroundColor Green
} else {
    Write-Host "WARNING: app did not report healthy within 30 s. Check $AppDir\server.log" -ForegroundColor Yellow
}

# Tailscale-only firewall rule for port 5000 (idempotent)
$fwRule = Get-NetFirewallRule -DisplayName 'ParkViewDrugs-Tailscale' -ErrorAction SilentlyContinue
if (-not $fwRule) {
    try {
        New-NetFirewallRule -DisplayName 'ParkViewDrugs-Tailscale' -Direction Inbound -Action Allow -Protocol TCP -LocalPort 5000 -InterfaceAlias 'Tailscale' | Out-Null
        Write-Host "[OK] Firewall rule 'ParkViewDrugs-Tailscale' created (Tailscale interface only)." -ForegroundColor Green
    } catch {
        Write-Host "WARNING: could not create firewall rule: $_" -ForegroundColor Yellow
    }
} else {
    Write-Host "[OK] Firewall rule 'ParkViewDrugs-Tailscale' already present." -ForegroundColor Green
}

# Daily database backup task (keeps newest 14 copies)
$BackupScript = Join-Path $AppDir 'backup_db.ps1'
if (Test-Path $BackupScript) {
    $bakAction = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$BackupScript`"" -WorkingDirectory $AppDir
    $bakTrigger = New-ScheduledTaskTrigger -Daily -At 3am
    $bakSettings = New-ScheduledTaskSettingsSet -StartWhenAvailable
    Register-ScheduledTask -TaskName 'ParkViewDrugsBackup' -Action $bakAction -Trigger $bakTrigger -Principal $Principal -Settings $bakSettings -Description 'Daily Park View Drugs database backup' -ErrorAction SilentlyContinue | Out-Null
    Write-Host "[OK] Daily backup task 'ParkViewDrugsBackup' registered (03:00, keeps 14 copies)." -ForegroundColor Green
}

# Verify
Start-Sleep -Seconds 2
$state = (Get-ScheduledTask -TaskName $TaskName).State
Write-Host "[OK] Task state: $state" -ForegroundColor Green

# Detect this machine's Tailscale IP for the access summary
$tsIP = (& tailscale ip -4 2>$null | Select-Object -First 1)
if (-not $tsIP) { $tsIP = "100.x.y.z" }

Write-Host ""
Write-Host "=== Access URLs ===" -ForegroundColor Green
Write-Host "  Local:      http://127.0.0.1:5000/"
Write-Host "  Tailscale:  http://$tsIP:5000/"
Write-Host "  Admin:      http://$tsIP:5000/admin/login"
Write-Host ""
Write-Host "Log file: $AppDir\server.log" -ForegroundColor Cyan
Write-Host ""

Stop-Transcript
