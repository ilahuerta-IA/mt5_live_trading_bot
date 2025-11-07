@echo off
REM ==============================================================================
REM MT5 TRADING BOT - LAUNCHER SCRIPT
REM ==============================================================================
REM This script runs the bot with error handling and automatic restart
REM ==============================================================================

echo.
echo ========================================================================
echo MT5 TRADING BOT - LAUNCHER
echo ========================================================================
echo.

REM Check if executable exists
if not exist "dist\MT5_Trading_Bot.exe" (
    echo [ERROR] Executable not found!
    echo Please run build_exe.bat first to create the executable.
    echo.
    pause
    exit /b 1
)

REM Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

REM Set log file with timestamp
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c-%%a-%%b)
for /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set mytime=%%a%%b)
set logfile=logs\bot_launcher_%mydate%_%mytime%.log

echo Starting MT5 Trading Bot...
echo Log file: %logfile%
echo Press Ctrl+C to stop the bot
echo.
echo ========================================================================
echo.

REM Run the bot and log output
:RESTART
echo [%date% %time%] Starting bot... >> %logfile%
dist\MT5_Trading_Bot.exe

REM Check exit code
if errorlevel 1 (
    echo [%date% %time%] Bot stopped with error code %errorlevel% >> %logfile%
    echo.
    echo [WARNING] Bot stopped with error!
    echo Check log file: %logfile%
    echo.
    echo Do you want to restart the bot? (Y/N)
    choice /c YN /n
    if errorlevel 2 goto END
    if errorlevel 1 (
        echo.
        echo Restarting bot in 5 seconds...
        timeout /t 5 /nobreak
        goto RESTART
    )
) else (
    echo [%date% %time%] Bot stopped normally >> %logfile%
    echo.
    echo Bot stopped normally.
)

:END
echo.
echo ========================================================================
echo Bot launcher closed
echo ========================================================================
echo.
pause
