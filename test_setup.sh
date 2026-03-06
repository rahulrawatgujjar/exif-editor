#!/bin/bash
# Test script to verify EXIF Editor installation

echo "🧪 Testing EXIF Editor Installation"
echo "=================================="
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
    fi
}

# Check if virtual environment exists
echo "1. Checking virtual environment..."
if [ -d "venv" ]; then
    print_status 0 "Virtual environment found"
else
    print_status 1 "Virtual environment not found"
    echo "   Run './setup.sh' first"
    exit 1
fi

# Check if virtual environment is activated or auto-detect
echo
echo "2. Checking Python environment..."
if python3 -c "import sys; print('Python executable:', sys.executable)" 2>/dev/null | grep -q "venv"; then
    print_status 0 "Virtual environment active"
else
    echo -e "${YELLOW}⚠️  Virtual environment not active, but auto-detection should work${NC}"
fi

# Check Python version
echo
echo "3. Checking Python version..."
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))' 2>/dev/null)
if [ $? -eq 0 ]; then
    REQUIRED_VERSION="3.8"
    if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then
        print_status 0 "Python $PYTHON_VERSION (compatible)"
    else
        print_status 1 "Python $PYTHON_VERSION (requires $REQUIRED_VERSION+)"
    fi
else
    print_status 1 "Cannot determine Python version"
fi

# Check dependencies
echo
echo "4. Checking dependencies..."
if python3 -c "import PIL; print('Pillow version:', PIL.__version__)" 2>/dev/null; then
    print_status 0 "Pillow installed"
else
    print_status 1 "Pillow not found"
fi

if python3 -c "import piexif; print('piexif available')" 2>/dev/null; then
    print_status 0 "piexif installed"
else
    print_status 1 "piexif not found"
fi

# Check camera presets
echo
echo "5. Checking camera presets..."
CAMERA_COUNT=$(python3 -c "from camera_presets import CAMERA_PRESETS; print(len(CAMERA_PRESETS))" 2>/dev/null)
if [ $? -eq 0 ]; then
    print_status 0 "$CAMERA_COUNT camera presets loaded"
else
    print_status 1 "Cannot load camera presets"
fi

# Check main scripts
echo
echo "6. Checking main scripts..."
if python3 -c "import exif_editor; print('exif_editor imports successfully')" 2>/dev/null; then
    print_status 0 "exif_editor.py loads correctly"
else
    print_status 1 "exif_editor.py has import errors"
fi

if python3 -c "import easy_run; print('easy_run imports successfully')" 2>/dev/null; then
    print_status 0 "easy_run.py loads correctly"
else
    print_status 1 "easy_run.py has import errors"
fi

# Test basic functionality
echo
echo "7. Testing basic functionality..."
if python3 exif_editor.py --help >/dev/null 2>&1; then
    print_status 0 "Command line interface works"
else
    print_status 1 "Command line interface failed"
fi

# Check for sample images
echo
echo "8. Checking sample data..."
if [ -d "input_images" ] && [ "$(ls input_images/*.jpg input_images/*.jpeg 2>/dev/null | wc -l)" -gt 0 ]; then
    IMAGE_COUNT=$(ls input_images/*.jpg input_images/*.jpeg 2>/dev/null | wc -l)
    print_status 0 "$IMAGE_COUNT sample images found"
else
    echo -e "${YELLOW}⚠️  No sample images found in input_images/${NC}"
    echo "   You can add JPEG images to test the functionality"
fi

echo
echo "=================================="
echo "🎉 Test complete!"
echo
echo "If all tests passed, you're ready to use EXIF Editor!"
echo
echo "Try these commands:"
echo "  python3 easy_run.py          # Interactive mode"
echo "  python3 exif_editor.py --help # Command line help"
echo
echo "For more information, see README.md"