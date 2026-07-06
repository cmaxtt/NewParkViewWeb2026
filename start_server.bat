@echo off
REM Park View Drugs — Waitress Server Launcher
REM This script is called by Windows Task Scheduler

cd /d "C:\aa-NewWeb"

REM Log file
set LOGFILE=C:\aa-NewWeb\server.log
echo %date% %time% — Starting Park View Drugs server >> %LOGFILE%

REM Start Waitress server
python run_prod.py >> %LOGFILE% 2>&1

echo %date% %time% — Server exited with code %errorlevel% >> %LOGFILE%
