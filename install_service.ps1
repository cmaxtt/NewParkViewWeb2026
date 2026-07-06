<#
.SYNOPSIS
    Installs Park View Drugs Flask app as a persistent Windows scheduled task.
    The task auto-starts at system boot and runs whether any user is logged in.
.DESCRIPTION
    Run this once as Administrator to register the task.
    The app will be available at http://100.104.147.60:5000/ on Tailscale
    even when Hermes/terminal is closed.
#>

$TaskName = "ParkViewDrugsServer"
$TaskPath = "C:\aa-NewWeb\start_server.bat"
$WorkingDir = "C:\aa-NewWeb"
$LogFile = "C:\aa-NewWeb\install.log"

Start-Transcript -Path $LogFile -Append

Write-Host "=== Park View Drugs — Persistent Server Installer ===" -ForegroundColor Green

# Check if running as Admin
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: Please run as Administrator (right-click > Run as Administrator)" -ForegroundColor Red
    pause
    exit 1
}

# Check Python exists
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "ERROR: Python not found in PATH" -ForegroundColor Red
    pause
    exit 1
}
Write-Host "[OK] Python found: $($python.Source)" -ForegroundColor Green

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

# Settings: restart on failure
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)

# Register
Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Principal $Principal -Settings $Settings -Description "Park View Drugs Flask app (Waitress) — persistent server"

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

# Verify
Start-Sleep -Seconds 3
$state = (Get-ScheduledTask -TaskName $TaskName).State
Write-Host "[OK] Task state: $state" -ForegroundColor Green

Write-Host ""
Write-Host "=== Access URLs ===" -ForegroundColor Green
Write-Host "  Local:      http://127.0.0.1:5000/"
Write-Host "  Tailscale:  http://100.104.147.60:5000/"
Write-Host "  Tailscale:  http://parkview:5000/"
Write-Host "  Admin:      http://100.104.147.60:5000/admin/login"
Write-Host ""
Write-Host "Log file: C:\aa-NewWeb\server.log" -ForegroundColor Cyan
Write-Host ""

Stop-Transcript
