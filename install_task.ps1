$TaskName = 'ParkViewDrugsServer'
# Resolve the app directory from this script's own location (distributable).
$AppDir = $PSScriptRoot
if ([string]::IsNullOrEmpty($AppDir)) { $AppDir = 'C:\aa-NewWeb' }
$PythonPath = Join-Path $AppDir '.venv\Scripts\python.exe'
$ScriptPath = Join-Path $AppDir 'run_prod.py'
$WorkDir = $AppDir

# Remove old task
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue

if (-not (Test-Path $PythonPath)) {
    throw "Missing $PythonPath. Create the virtual environment and install requirements first."
}

# Create task
$Action = New-ScheduledTaskAction -Execute $PythonPath -Argument $ScriptPath -WorkingDirectory $WorkDir
$Trigger = New-ScheduledTaskTrigger -AtStartup
$Principal = New-ScheduledTaskPrincipal -UserId 'SYSTEM' -LogonType ServiceAccount -RunLevel Highest
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1) -ExecutionTimeLimit 0

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Principal $Principal -Settings $Settings -Description 'Park View Drugs Flask app (Waitress)'

Write-Host "Task '$TaskName' installed. Starting now..."
Start-ScheduledTask -TaskName $TaskName
Start-Sleep -Seconds 3

$state = (Get-ScheduledTask -TaskName $TaskName).State
Write-Host "Task state: $state"

# Test if responding
try {
    $r = Invoke-WebRequest -Uri 'http://127.0.0.1:5050/' -TimeoutSec 5 -UseBasicParsing
    Write-Host "App responding: HTTP $($r.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "App not yet responding (may need a few seconds)..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Access ===" -ForegroundColor Green
$tsIP = (& tailscale ip -4 2>$null | Select-Object -First 1)
if (-not $tsIP) { $tsIP = "100.x.y.z" }
Write-Host "  Local:      http://127.0.0.1:5050/"
Write-Host "  Tailscale:  http://$tsIP:5050/"
Write-Host "  Admin:      http://$tsIP:5050/admin/login"
