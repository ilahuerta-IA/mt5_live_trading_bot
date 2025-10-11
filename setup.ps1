# MT5 Live Trading Bot Setup Script
# ==================================
# Automated setup for MetaTrader 5 live trading integration

Write-Host "🌅 MT5 LIVE TRADING BOT SETUP" -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan
Write-Host ""

# Set error handling
$ErrorActionPreference = "Continue"

# Get project directory
$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectDir

Write-Host "📁 Project Directory: $projectDir" -ForegroundColor Green
Write-Host ""

# Step 1: Check Python installation
Write-Host "🔧 STEP 1: Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.8+ first." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Step 2: Create virtual environment (optional but recommended)
Write-Host ""
Write-Host "🔧 STEP 2: Virtual environment setup..." -ForegroundColor Yellow
$createVenv = Read-Host "Create virtual environment for MT5 bot? (y/n)"

if ($createVenv -eq "y" -or $createVenv -eq "Y") {
    Write-Host "Creating virtual environment..." -ForegroundColor Blue
    python -m venv venv_mt5_bot
    
    Write-Host "Activating virtual environment..." -ForegroundColor Blue
    .\venv_mt5_bot\Scripts\Activate.ps1
    
    Write-Host "✅ Virtual environment created and activated" -ForegroundColor Green
} else {
    Write-Host "⚠️  Using system Python environment" -ForegroundColor Yellow
}

# Step 3: Install MT5 requirements
Write-Host ""
Write-Host "🔧 STEP 3: Installing MT5 requirements..." -ForegroundColor Yellow
Write-Host "Installing MetaTrader5 package..." -ForegroundColor Blue

try {
    pip install MetaTrader5
    Write-Host "✅ MetaTrader5 package installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to install MetaTrader5 package" -ForegroundColor Red
    Write-Host "💡 Try running as administrator or check internet connection" -ForegroundColor Yellow
}

Write-Host "Installing additional requirements..." -ForegroundColor Blue
try {
    pip install -r requirements.txt
    Write-Host "✅ Additional requirements installed" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Some requirements may have failed to install" -ForegroundColor Yellow
    Write-Host "💡 Check requirements.txt and install manually if needed" -ForegroundColor Yellow
}

# Step 4: Verify directory structure
Write-Host ""
Write-Host "🔧 STEP 4: Verifying directory structure..." -ForegroundColor Yellow

$requiredDirs = @("config", "logs", "src", "strategies")
foreach ($dir in $requiredDirs) {
    if (Test-Path $dir) {
        Write-Host "✅ Directory exists: $dir" -ForegroundColor Green
    } else {
        Write-Host "❌ Missing directory: $dir" -ForegroundColor Red
    }
}

# Step 5: Setup configuration
Write-Host ""
Write-Host "🔧 STEP 5: Setting up configuration..." -ForegroundColor Yellow

# Copy credentials template if needed
if (!(Test-Path "config\mt5_credentials.json")) {
    if (Test-Path "config\mt5_credentials_template.json") {
        Copy-Item "config\mt5_credentials_template.json" "config\mt5_credentials.json"
        Write-Host "✅ Created credentials file from template" -ForegroundColor Green
        Write-Host "⚠️  Please edit config\mt5_credentials.json with your MT5 account details" -ForegroundColor Yellow
    } else {
        Write-Host "❌ Template file not found" -ForegroundColor Red
    }
} else {
    Write-Host "✅ Credentials file already exists" -ForegroundColor Green
}

# Step 6: Test MT5 setup
Write-Host ""
Write-Host "🔧 STEP 6: Testing MT5 setup..." -ForegroundColor Yellow

$testSetup = Read-Host "Run MT5 setup tests now? (y/n)"

if ($testSetup -eq "y" -or $testSetup -eq "Y") {
    Write-Host "Running MT5 setup tests..." -ForegroundColor Blue
    python test_setup.py
} else {
    Write-Host "⚠️  Setup tests skipped" -ForegroundColor Yellow
    Write-Host "💡 Run 'python test_setup.py' later to verify setup" -ForegroundColor Yellow
}

# Step 7: Instructions
Write-Host ""
Write-Host "🎉 MT5 LIVE TRADING BOT SETUP COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "📋 NEXT STEPS:" -ForegroundColor Cyan
Write-Host "1. Download and install MetaTrader 5 terminal from your broker" -ForegroundColor White
Write-Host "2. Create a demo account for testing" -ForegroundColor White
Write-Host "3. Update config\mt5_credentials.json with your MT5 login details" -ForegroundColor White
Write-Host "4. Run 'python test_setup.py' to verify connection" -ForegroundColor White
Write-Host "5. Test signal generation: 'python src\sunrise_signal_adapter.py'" -ForegroundColor White
Write-Host "6. Start live trading: 'python src\mt5_live_trading_connector.py'" -ForegroundColor White
Write-Host ""
Write-Host "🔗 STRATEGY CONNECTION:" -ForegroundColor Cyan
Write-Host "This bot connects to your existing Sunrise strategies in:" -ForegroundColor White
Write-Host "..\quant_bot_project\src\strategies (relative to Portfolio folder)" -ForegroundColor Gray
Write-Host ""
Write-Host "🚨 SAFETY REMINDERS:" -ForegroundColor Red
Write-Host "- ALWAYS test on demo account first" -ForegroundColor White
Write-Host "- Start with small position sizes" -ForegroundColor White
Write-Host "- Never risk more than you can afford to lose" -ForegroundColor White
Write-Host "- This is educational code - test thoroughly" -ForegroundColor White
Write-Host "- Demo mode is enforced by default" -ForegroundColor White
Write-Host ""

# Optional: Open files for editing
$openFiles = Read-Host "Open key files for editing? (y/n)"

if ($openFiles -eq "y" -or $openFiles -eq "Y") {
    Write-Host "Opening files..." -ForegroundColor Blue
    
    # Open credentials file
    if (Test-Path "config\mt5_credentials.json") {
        notepad "config\mt5_credentials.json"
    }
    
    # Open main connector
    if (Test-Path "src\mt5_live_trading_connector.py") {
        code "src\mt5_live_trading_connector.py" 2>$null
    }
}

Write-Host ""
Write-Host "🌅 Ready for live trading! Happy trading! 🚀" -ForegroundColor Cyan
Read-Host "Press Enter to exit"