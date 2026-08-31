@echo off
REM Park View Drugs - Waitress Server Launcher
REM This script is called by Windows Task Scheduler
REM Location-agnostic: resolves the app dir from this script's own path.

cd /d "%~dp0"

REM Log file (rotate at 5 MB so it cannot grow forever)
set LOGFILE=%~dp0server.log
if exist "%LOGFILE%" (
    for %%A in ("%LOGFILE%") do if %%~zA GTR 5242880 (
        move /y "%LOGFILE%" "%~dp0server.log.old" >nul 2>&1
    )
)
echo %date% %time% - Starting Park View Drugs server >> %LOGFILE%

REM Use the installation's virtual environment instead of an arbitrary PATH python.
if exist "%~dp0.venv\Scripts\python.exe" (
    "%~dp0.venv\Scripts\python.exe" run_prod.py >> %LOGFILE% 2>&1
) else (
    echo ERROR: .venv is missing next to %~dp0. Run the setup instructions first. >> %LOGFILE%
    exit /b 1
)

echo %date% %time% - Server exited with code %errorlevel% >> %LOGFILE%
