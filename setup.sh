#!/bin/bash
# Setup script for EXIF Editor with virtual environment

set -e  # Exit on any error

echo "🚀 Setting up EXIF Editor with virtual environment..."
echo

# Function to check command availability
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if Python 3 is available
if ! command_exists python3; then
    echo "❌ Python 3 is not installed or not in PATH."
    echo "   Please install Python 3.8+ from https://python.org"
    echo "   Then run this script again."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python $PYTHON_VERSION detected. Python $REQUIRED_VERSION or higher is required."
    exit 1
fi

echo "✅ Python $PYTHON_VERSION found"

# Check if virtual environment already exists
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists."
    read -p "   Remove and recreate? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🗑️  Removing existing virtual environment..."
        rm -rf venv
    else
        echo "📦 Using existing virtual environment..."
        echo "🔧 Activating and checking dependencies..."
        source venv/bin/activate
        if ! python3 -c "import PIL, piexif" 2>/dev/null; then
            echo "📥 Installing/updating dependencies..."
            pip install --upgrade pip
            pip install -r requirements.txt
        else
            echo "✅ Dependencies already installed"
        fi
        echo
        echo "🎉 Setup complete!"
        echo
        echo "To use the interactive EXIF editor:"
        echo "  python3 easy_run.py"
        echo
        echo "Or activate the virtual environment manually:"
        echo "  source venv/bin/activate"
        echo "  python3 exif_editor.py --help"
        exit 0
    fi
fi

echo "📦 Creating virtual environment..."
python3 -m venv venv

echo "🔧 Activating virtual environment..."
source venv/bin/activate

echo "⬆️  Upgrading pip..."
pip install --upgrade pip

echo "📥 Installing dependencies..."
pip install -r requirements.txt

echo
echo "🧪 Testing installation..."
if python3 -c "import PIL, piexif; print('✅ All dependencies installed successfully')"; then
    echo "✅ Setup completed successfully!"
    echo
    echo "🎯 Quick start:"
    echo "  python3 easy_run.py    # Interactive mode"
    echo "  python3 exif_editor.py --help    # Command line help"
    echo
    echo "📚 For more information, see README.md"
    echo
    echo "💡 Pro tip: The virtual environment is automatically detected,"
    echo "   so you can run the scripts directly without manual activation!"
else
    echo "❌ Setup failed. Please check the error messages above."
    exit 1
fi
echo "To run with the virtual environment launcher:"
echo "  ./run_with_venv.sh python3 easy_run.py"