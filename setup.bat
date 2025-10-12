@echo off
REM MCP Proxy Server Setup Script for Windows
REM This script sets up the virtual environment and installs dependencies

echo 🚀 Setting up MCP Proxy Server...

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python is required but not found.
    echo Please install Python and try again.
    pause
    exit /b 1
)

echo ✅ Python found
python --version

REM Create virtual environment
echo 📦 Creating virtual environment...
if exist venv (
    echo ⚠️  Virtual environment already exists. Removing old one...
    rmdir /s /q venv
)

python -m venv venv

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo 📈 Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo 📚 Installing dependencies...
pip install -r requirements.txt

echo.
echo ✅ Setup complete!
echo.
echo To use the MCP Proxy Server:
echo 1. Activate the virtual environment:
echo    venv\Scripts\activate
echo.
echo 2. Run the proxy server:
echo    python -m src.translation_helps_mcp_proxy
echo.
echo 3. For debug mode:
echo    python -m src.translation_helps_mcp_proxy --debug
echo.
echo 4. To use a different upstream URL:
echo    python -m src.translation_helps_mcp_proxy --upstream-url "http://localhost:5173/api/mcp"
echo.
echo For more information, see README.md
pause