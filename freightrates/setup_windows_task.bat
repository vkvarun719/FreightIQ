@echo off
rem ==============================================================================
rem setup_windows_task.bat - Register Windows Task Scheduler job for Daily BDI Scrape
rem ==============================================================================

setlocal enabledelayedexpansion
set "TASK_NAME=BDI_Freight_Daily_Update"
set "BAT_PATH=%~dp0run_daily_update.bat"
set "RUN_TIME=18:30"

echo ==============================================================================
echo   BALTIC DRY INDEX (BDI) - WINDOWS TASK SCHEDULER INSTALLER
echo ==============================================================================
echo.
echo Target Batch Script: %BAT_PATH%
echo Scheduled Time     : Daily at %RUN_TIME% (Post-London Baltic Settlement)
echo.

rem Register the task using Windows schtasks command
schtasks /Create /TN "%TASK_NAME%" /TR "\"%BAT_PATH%\"" /SC DAILY /ST %RUN_TIME% /F

if %ERRORLEVEL% equ 0 (
    echo.
    echo [SUCCESS] Scheduled Task "%TASK_NAME%" successfully registered!
    echo It will execute daily at %RUN_TIME% silently in the background.
    echo To view logs, inspect: %~dp0logs\scraper.log
    echo.
    echo To test run immediately via Task Scheduler:
    echo   schtasks /Run /TN "%TASK_NAME%"
    echo.
    echo To delete the scheduled task anytime:
    echo   schtasks /Delete /TN "%TASK_NAME%" /F
) else (
    echo.
    echo [ERROR] Failed to register scheduled task. If prompted, please run as Administrator.
)

echo.
pause
