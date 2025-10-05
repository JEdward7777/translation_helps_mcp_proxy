#!/bin/bash

# MCP Proxy Server Setup Script
# This script sets up the virtual environment and installs dependencies

set -e  # Exit on any error

echo "🚀 Setting up MCP Proxy Server..."

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is required but not found."
    echo "Please install Python 3 and try again."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists. Removing old one..."
    rm -rf venv
fi

python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📈 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "To use the MCP Proxy Server:"
echo "1. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Run the proxy server:"
echo "   python mcp_proxy_server.py"
echo ""
echo "3. For debug mode:"
echo "   python mcp_proxy_server.py --debug"
echo ""
echo "4. To use a different upstream URL:"
echo "   python mcp_proxy_server.py --upstream-url 'http://localhost:5173/api/mcp'"
echo ""
echo "For more information, see README.md"