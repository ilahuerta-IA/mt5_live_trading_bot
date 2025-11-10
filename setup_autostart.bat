@echo off
REM ===================================================================
REM MT5 Trading Bot - Auto-Start Setup
REM Creates Windows Task Scheduler entry for automatic bot launch
REM ===================================================================

echo.
echo ========================================
echo  MT5 Trading Bot Auto-Start Setup
echo ========================================
echo.
echo This will configure Windows to automatically start the bot when you log in.
echo.
pause

REM Get current directory
set "SCRIPT_DIR=%~dp0"
set "BOT_LAUNCHER=%SCRIPT_DIR%run_bot.bat"

echo.
echo Creating scheduled task...
echo.

REM Create task that runs at user login
schtasks /create /tn "MT5_Trading_Bot_AutoStart" /tr "\"%BOT_LAUNCHER%\"" /sc onlogon /rl highest /f

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo  SUCCESS!
    echo ========================================
    echo.
    echo The bot will now start automatically when you log into Windows.
    echo.
    echo To verify: Open Task Scheduler and look for "MT5_Trading_Bot_AutoStart"
    echo.
    echo To remove auto-start later, run: remove_autostart.bat
    echo.
) else (
    echo.
    echo ========================================
    echo  ERROR
    echo ========================================
    echo.
    echo Failed to create scheduled task. Make sure you run this as Administrator.
    echo Right-click this file and select "Run as administrator"
    echo.
)

pause
