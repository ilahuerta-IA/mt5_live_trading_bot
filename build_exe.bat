@echo off
REM ==============================================================================
REM MT5 TRADING BOT - BUILD EXECUTABLE
REM ==============================================================================
REM This script creates a standalone .exe file that can run without Python/VS Code
REM ==============================================================================

echo.
echo ========================================================================
echo MT5 TRADING BOT - EXECUTABLE BUILDER
echo ========================================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.8+ and try again.
    pause
    exit /b 1
)

echo [1/5] Checking Python installation...
python --version
echo.

REM Check if PyInstaller is installed
echo [2/5] Checking PyInstaller...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
    if errorlevel 1 (
        echo [ERROR] Failed to install PyInstaller!
        pause
        exit /b 1
    )
)
echo PyInstaller is ready.
echo.

REM Clean previous build artifacts
echo [3/5] Cleaning previous build artifacts...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "*.spec" del /q "*.spec"
echo Clean completed.
echo.

REM Build the executable
echo [4/5] Building executable... (This may take 1-2 minutes)
echo.
pyinstaller --onefile ^
    --name "MT5_Trading_Bot" ^
    --noconsole ^
    --icon=NONE ^
    --add-data "strategies;strategies" ^
    --hidden-import=MetaTrader5 ^
    --hidden-import=pandas ^
    --hidden-import=numpy ^
    --hidden-import=tkinter ^
    advanced_mt5_monitor_gui.py

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed!
    echo Check the error messages above.
    pause
    exit /b 1
)

echo.
echo [5/5] Build completed successfully!
echo.
echo ========================================================================
echo BUILD SUMMARY
echo ========================================================================
echo Executable location: dist\MT5_Trading_Bot.exe
echo Size: 
dir "dist\MT5_Trading_Bot.exe" | find "MT5_Trading_Bot.exe"
echo.
echo ========================================================================
echo DEPLOYMENT INSTRUCTIONS
echo ========================================================================
echo 1. Copy dist\MT5_Trading_Bot.exe to your desired location
echo 2. Ensure MetaTrader 5 terminal is installed
echo 3. Run MT5_Trading_Bot.exe
echo 4. Logs will be created in the same directory as the .exe
echo.
echo NOTE: The .exe file is NOT committed to Git (protected by .gitignore)
echo ========================================================================
echo.

REM Clean up build artifacts but keep dist folder
echo Cleaning temporary build files...
if exist "build" rmdir /s /q "build"
if exist "MT5_Trading_Bot.spec" del /q "MT5_Trading_Bot.spec"
echo.

echo Build process completed! Press any key to exit...
pause >nul
