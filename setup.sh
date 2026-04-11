#!/bin/bash

# Universal File Converter - Setup Script
# This script automates the installation process

set -e

echo "=========================================="
echo "Universal File Converter - Setup"
echo "=========================================="
echo ""

# Check OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "✓ Detected Linux OS"
    PKG_MANAGER="apt-get"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "✓ Detected macOS"
    PKG_MANAGER="brew"
else
    echo "✗ Unsupported OS: $OSTYPE"
    exit 1
fi

# Check if running as root (for Linux)
if [[ "$OSTYPE" == "linux-gnu"* ]] && [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root (use sudo)" 
   exit 1
fi

# Install system dependencies
echo ""
echo "Step 1: Installing system dependencies..."
echo "=========================================="

if [[ "$PKG_MANAGER" == "apt-get" ]]; then
    apt-get update
    apt-get install -y \
        python3 \
        python3-pip \
        python3-venv \
        python3-dev \
        libreoffice \
        ffmpeg \
        imagemagick \
        tesseract-ocr \
        tesseract-ocr-eng \
        poppler-utils \
        libmagic1
    
    echo "✓ System dependencies installed"
    
    # Optional: Install additional Tesseract languages
    read -p "Install additional OCR languages? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        apt-get install -y \
            tesseract-ocr-spa \
            tesseract-ocr-fra \
            tesseract-ocr-deu \
            tesseract-ocr-ita \
            tesseract-ocr-por
        echo "✓ Additional languages installed"
    fi
    
elif [[ "$PKG_MANAGER" == "brew" ]]; then
    brew install \
        python3 \
        libreoffice \
        ffmpeg \
        imagemagick \
        tesseract \
        poppler \
        libmagic
    
    echo "✓ System dependencies installed"
fi

# Create virtual environment
echo ""
echo "Step 2: Creating Python virtual environment..."
echo "=========================================="

python3 -m venv venv
echo "✓ Virtual environment created"

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo ""
echo "Step 3: Upgrading pip..."
echo "=========================================="
pip install --upgrade pip
echo "✓ pip upgraded"

# Install Python dependencies
echo ""
echo "Step 4: Installing Python dependencies..."
echo "=========================================="
pip install -r requirements.txt
echo "✓ Python dependencies installed"

# Create necessary directories
echo ""
echo "Step 5: Creating directories..."
echo "=========================================="
mkdir -p uploads outputs temp
echo "✓ Directories created"

# Verify installations
echo ""
echo "Step 6: Verifying installations..."
echo "=========================================="

verify_command() {
    if command -v $1 &> /dev/null; then
        echo "✓ $1 is installed"
        return 0
    else
        echo "✗ $1 is NOT installed"
        return 1
    fi
}

verify_command python3
verify_command libreoffice
verify_command ffmpeg
verify_command convert  # ImageMagick
verify_command tesseract
verify_command pdfinfo  # Poppler

# Test Python imports
echo ""
echo "Testing Python imports..."
python3 -c "import flask; print('✓ Flask')"
python3 -c "import PyPDF2; print('✓ PyPDF2')"
python3 -c "import PIL; print('✓ Pillow')"
python3 -c "import pytesseract; print('✓ pytesseract')"

echo ""
echo "=========================================="
echo "✓ Setup Complete!"
echo "=========================================="
echo ""
echo "To start the application:"
echo "  1. Activate virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Run the application:"
echo "     python app.py"
echo ""
echo "  3. Open browser to:"
echo "     http://localhost:5000"
echo ""
echo "For production deployment, see README.md"
echo "=========================================="