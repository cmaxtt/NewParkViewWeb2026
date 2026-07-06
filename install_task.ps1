$TaskName = 'ParkViewDrugsServer'
$PythonPath = 'C:\Users\cmaxt\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe'
$ScriptPath = 'C:\aa-NewWeb\run_prod.py'
$WorkDir = 'C:\aa-NewWeb'

# Remove old task
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue

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
    $r = Invoke-WebRequest -Uri 'http://127.0.0.1:5000/' -TimeoutSec 5 -UseBasicParsing
    Write-Host "App responding: HTTP $($r.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "App not yet responding (may need a few seconds)..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Access ===" -ForegroundColor Green
Write-Host "  Local:      http://127.0.0.1:5000/"
Write-Host "  Tailscale:  http://100.104.147.60:5000/"
Write-Host "  Admin:      http://100.104.147.60:5000/admin/login"
