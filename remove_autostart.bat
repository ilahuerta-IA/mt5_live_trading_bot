@echo off
REM ===================================================================
REM MT5 Trading Bot - Remove Auto-Start
REM Removes Windows Task Scheduler entry
REM ===================================================================

echo.
echo ========================================
echo  Remove MT5 Bot Auto-Start
echo ========================================
echo.
echo This will remove the automatic bot startup from Windows login.
echo.
pause

echo.
echo Removing scheduled task...
echo.

schtasks /delete /tn "MT5_Trading_Bot_AutoStart" /f

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo  SUCCESS!
    echo ========================================
    echo.
    echo Auto-start has been removed.
    echo You will need to manually launch the bot from now on.
    echo.
) else (
    echo.
    echo ========================================
    echo  ERROR
    echo ========================================
    echo.
    echo Task not found or deletion failed.
    echo.
)

pause
