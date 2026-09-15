@echo off
rem ==============================================================================
rem run_daily_update.bat - Baltic Dry Index (BDI) Automated Daily Scraping & Retraining
rem ==============================================================================

setlocal enabledelayedexpansion
cd /d "%~dp0freightrates"

if not exist logs mkdir logs

echo ======================================================== >> logs\scraper.log
echo BDI AUTO-UPDATE RUN STARTED: %DATE% %TIME% >> logs\scraper.log
echo ======================================================== >> logs\scraper.log

rem Run canonical live scraper and model retraining
python bdi_live_scraper.py --run-now >> logs\scraper.log 2>&1

if %ERRORLEVEL% equ 0 (
    echo BDI Auto-Update completed successfully at %TIME% >> logs\scraper.log
) else (
    echo BDI Auto-Update encountered error level %ERRORLEVEL% at %TIME% >> logs\scraper.log
)

echo. >> logs\scraper.log
