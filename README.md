# 📸 EXIF Editor — Image Metadata Tool

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](CONTRIBUTING.md)

A powerful command-line tool to **view, edit, fake, clear, copy, export and import** EXIF metadata for JPEG images. Perfect for AI-generated images, photography workflows, and metadata management.

## ✨ Features

- 🎭 **Fake Camera Profiles**: Apply realistic camera metadata to AI-generated images
- 📱 **16+ Camera Presets**: Professional DSLRs, mirrorless cameras, and smartphones
- 🌍 **GPS Location**: Add location data via city names or coordinates
- 📅 **Timestamp Control**: Random or fixed date/time metadata
- 🔄 **Batch Processing**: Process entire folders of images
- 🛡️ **Virtual Environment**: Isolated Python environment for clean dependencies
- 🎯 **Interactive Mode**: User-friendly prompts for easy usage

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/exif-editor.git
cd exif-editor
```

### 2. Test Your Setup

Verify everything works correctly:

```bash
./test_setup.sh
```

This will check:
- ✅ Virtual environment
- ✅ Python version compatibility
- ✅ Dependencies installation
- ✅ Camera presets loading
- ✅ Script functionality

### 3. Start Using EXIF Editor

```bash
# Interactive mode (recommended for beginners)
python3 easy_run.py

# Command line mode (advanced users)
python3 exif_editor.py fake image.jpg --city "Paris"
```

Follow the prompts to configure your EXIF metadata!

## 📋 Prerequisites

- **Python 3.8+** (check with `python3 --version`)
- **Internet connection** (for geocoding city names to GPS coordinates)
- **JPEG images** (`.jpg`, `.jpeg`, `.jpe`, `.jfif` formats supported)

### System Requirements

| OS | Requirements |
|----|-------------|
| **Linux/macOS** | Bash shell, standard Python installation |
| **Windows** | PowerShell or Git Bash, Python 3.8+ |

## 🛠️ Installation

### Option 1: Automated Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/exif-editor.git
cd exif-editor

# Run setup script
./setup.sh
```

### Option 2: Manual Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/exif-editor.git
cd exif-editor

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Option 3: Global Installation

```bash
# Install dependencies globally (not recommended)
pip install Pillow piexif

# Run without virtual environment
python3 exif_editor.py --help
```

## � Repository Structure

```
exif-editor/
├── 📄 README.md              # This file - comprehensive documentation
├── 📄 LICENSE                 # MIT License
├── 📄 CONTRIBUTING.md         # Guidelines for contributors
├── 📄 requirements.txt        # Python dependencies
├── 📄 .gitignore             # Git ignore rules
├── 🚀 setup.sh               # Automated setup script
├── 🧪 test_setup.sh          # Installation verification script
├── 🏃 run_with_venv.sh       # Virtual environment launcher
├── 📷 exif_editor.py         # Main EXIF editing tool
├── 🎯 easy_run.py            # Interactive wrapper script
├── 📸 camera_presets.py      # Camera and phone presets
├── 🐍 python_venv.py         # Python virtual environment launcher
├── 📁 input_images/          # Sample images directory
├── 📁 output_images/         # Output directory (created automatically)
└── 🗂️  venv/                 # Virtual environment (created by setup.sh)
```

### Command Line Mode (Advanced)

```bash
# Basic usage - random camera profile
python3 exif_editor.py fake image.jpg

# Advanced usage with all options
python3 exif_editor.py fake ./input_images/ \
  --preset sony_a7iv \
  --random \
  --city "Tokyo" \
  --title "Urban Photography" \
  --artist "Jane Doe" \
  --days-back 30 \
  --output-dir ./output/
```

## 📚 Commands Overview

| Command | Description | Use Case |
|---------|-------------|----------|
| `fake` | Apply complete fake camera profile | AI-generated images |
| `view` | Display all EXIF metadata | Inspect image data |
| `edit` | Set specific EXIF fields | Manual metadata editing |
| `clear` | Remove all EXIF metadata | Privacy protection |
| `copy` | Copy EXIF between images | Metadata transfer |
| `export` | Save metadata to JSON | Backup/inspection |
| `import` | Load metadata from JSON | Restore metadata |
| `gps` | Set GPS coordinates | Location tagging |

## 🎭 Camera Presets

### Professional Cameras
- **Canon EOS R5** - Full-frame mirrorless with RF lenses
- **Nikon Z 7II** - High-resolution mirrorless with Z-mount lenses
- **Sony A7 IV** - Versatile full-frame camera with FE lenses
- **Fujifilm X-T5** - APS-C camera with XF lenses

### Smartphone Cameras
- **iPhone 15 Pro** - Apple's latest flagship camera
- **iPhone 15 Pro Max** - Larger sensor variant
- **Samsung Galaxy S24** - Android flagship with advanced camera
- **Samsung Galaxy S24 Ultra** - Premium Android camera
- **Google Pixel 9** - Computational photography expert
- **Google Pixel 9 Pro** - Professional-grade Pixel camera
- **OnePlus 12** - Hasselblad partnership camera
- **Xiaomi 14** - Leica collaboration camera
- **Xiaomi 14 Ultra** - Premium Xiaomi camera
- **OPPO Find X7** - Hasselblad camera system
- **HONOR Magic6 Pro** - Advanced Android camera
- **Vivo X100 Ultra** - Zeiss optics camera

## 📖 Detailed Usage Examples

### Single Image Processing

```bash
# Random camera profile
python3 exif_editor.py fake photo.jpg

# Specific camera with randomization
python3 exif_editor.py fake photo.jpg -p canon_r5 --random

# With location and metadata
python3 exif_editor.py fake photo.jpg \
  --city "Paris" \
  --title "Eiffel Tower" \
  --artist "John Doe" \
  --copyright "© 2024 John Doe"
```

### Batch Processing

```bash
# Process entire folder
python3 exif_editor.py fake ./input_images/ -d ./output/

# Random cameras with city location
python3 exif_editor.py fake ./input_images/ \
  --random \
  --city "New York" \
  -d ./output/
```

### Manual Metadata Editing

```bash
# Set specific fields
python3 exif_editor.py edit photo.jpg \
  --make "Canon" \
  --model "EOS R5" \
  --artist "Jane Smith" \
  --iso 400 \
  --f-number "2.8"
```

### GPS and Location

```bash
# By city name (automatic geocoding)
python3 exif_editor.py fake photo.jpg --city "London"

# Manual coordinates
python3 exif_editor.py gps photo.jpg --lat 51.5074 --lon -0.1278

# With altitude
python3 exif_editor.py gps photo.jpg --lat 51.5074 --lon -0.1278 --alt 25
```

## 🔧 Configuration

### Virtual Environment

The project automatically detects and uses the virtual environment. Manual activation:

```bash
# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### Custom Camera Presets

Add new cameras by editing `camera_presets.py`:

```python
CAMERA_PRESETS = {
    "my_camera": {
        "make": "MyBrand",
        "model": "MyModel",
        "lens_make": "MyBrand",
        "software": "MySoftware",
        "lenses": [
            ("My Lens 50mm f/1.8", 50, (18, 10), [(18,10),(20,10),(28,10)]),
        ],
        "iso_pool": [100, 200, 400, 800],
        "shutter_pool": [(1,4000),(1,2000),(1,1000),(1,500)],
    }
}
```

## 🐛 Troubleshooting

### Common Issues

**"Missing dependencies" error:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt
```

**"City not found" error:**
- Check internet connection
- Try different city name spelling
- Use manual GPS coordinates instead

**"Permission denied" on setup.sh:**
```bash
chmod +x setup.sh
./setup.sh
```

### Getting Help

```bash
# View all commands
python3 exif_editor.py --help

# View specific command help
python3 exif_editor.py fake --help
python3 exif_editor.py edit --help
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Add camera presets to `camera_presets.py`
5. Test your changes
6. Submit a pull request

### Adding New Camera Presets

Please follow the existing format in `camera_presets.py`. Include:
- Realistic camera specifications
- Accurate lens information
- Appropriate ISO and shutter speed ranges
- Proper software names

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Pillow](https://python-pillow.org/) - Python Imaging Library
- [piexif](https://github.com/hMatoba/piexif) - EXIF manipulation library
- [OpenStreetMap Nominatim](https://nominatim.openstreetmap.org/) - Geocoding service

## 📞 Support

- 📧 Create an [issue](https://github.com/yourusername/exif-editor/issues) for bugs
- 💡 Request [features](https://github.com/yourusername/exif-editor/issues) you'd like to see
- 📖 Check the [wiki](https://github.com/yourusername/exif-editor/wiki) for advanced usage

---

**Made with ❤️ for photographers, AI artists, and metadata enthusiasts**
