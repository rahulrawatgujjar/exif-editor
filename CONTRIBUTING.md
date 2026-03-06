# Contributing to EXIF Editor

Thank you for your interest in contributing to EXIF Editor! 🎉

We welcome contributions from everyone. This document provides guidelines and information for contributors.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Adding Camera Presets](#adding-camera-presets)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Style Guidelines](#style-guidelines)

## 🤝 Code of Conduct

This project follows a code of conduct to ensure a welcoming environment for all contributors. By participating, you agree to:

- Be respectful and inclusive
- Focus on constructive feedback
- Accept responsibility for mistakes
- Show empathy towards other contributors
- Help create a positive community

## 🚀 Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/rahulrawatgujjar/exif-editor.git
   cd exif-editor
   ```
3. **Set up the development environment**:
   ```bash
   ./setup.sh
   ```
4. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 💡 How to Contribute

### Types of Contributions

- 🐛 **Bug fixes** - Fix existing issues
- ✨ **Features** - Add new functionality
- 📚 **Documentation** - Improve docs, README, comments
- 🎨 **UI/UX** - Improve user interface and experience
- 🧪 **Tests** - Add or improve tests
- 📦 **Camera Presets** - Add new camera profiles

### Finding Issues

- Check the [Issues](https://github.com/rahulrawatgujjar/exif-editor/issues) page
- Look for issues labeled `good first issue` or `help wanted`
- Comment on issues you'd like to work on

## 🛠️ Development Setup

### Prerequisites

- Python 3.8+
- Git
- Internet connection (for geocoding features)

### Setup Steps

1. **Clone and setup**:
   ```bash
   git clone https://github.com/rahulrawatgujjar/exif-editor.git
   cd exif-editor
   ./setup.sh
   ```

2. **Verify installation**:
   ```bash
   python3 exif_editor.py --help
   python3 easy_run.py  # Test interactive mode
   ```

## 📷 Adding Camera Presets

Camera presets are stored in `camera_presets.py`. To add a new camera:

### 1. Research Camera Specifications

Gather accurate information about:
- Camera make and model
- Lens information (focal length, aperture, manufacturer)
- Typical ISO ranges
- Common shutter speeds
- Software used for processing

### 2. Add to camera_presets.py

```python
CAMERA_PRESETS = {
    "your_camera_preset": {
        "make": "Camera Brand",
        "model": "Camera Model",
        "lens_make": "Lens Brand",
        "software": "Software Name",
        "lenses": [
            # (name, focal_length, base_aperture, aperture_range)
            ("Lens Name 50mm f/1.8", 50, (18, 10), [(18,10), (20,10), (28,10), (40,10)]),
        ],
        "iso_pool": [100, 200, 400, 800, 1600, 3200],
        "shutter_pool": [(1,4000), (1,2000), (1,1000), (1,500), (1,250), (1,125)],
    }
}
```

### 3. Lens Format Explanation

Each lens tuple contains:
- **Name**: Full lens name as it appears in EXIF
- **Focal Length**: Numeric focal length in mm
- **Base Aperture**: (numerator, denominator) for the lens's maximum aperture
- **Aperture Range**: List of available f-stops as (numerator, denominator) tuples

### 4. Testing Your Preset

```bash
# Test with your new preset
python3 exif_editor.py fake test_image.jpg -p your_camera_preset

# View the results
python3 exif_editor.py view test_image.jpg
```

## 🧪 Testing

### Running Tests

```bash
# Run basic functionality tests
python3 -c "from exif_editor import CAMERA_PRESETS; print(f'Loaded {len(CAMERA_PRESETS)} presets')"

# Test with sample images
python3 exif_editor.py fake input_images/sample.jpg -p random -d output/
```

### Manual Testing Checklist

- [ ] Single image processing works
- [ ] Batch processing works
- [ ] All camera presets load correctly
- [ ] GPS geocoding works (requires internet)
- [ ] Manual GPS coordinates work
- [ ] Export/import functionality works
- [ ] Interactive mode works

## 📝 Submitting Changes

### 1. Commit Your Changes

```bash
# Stage your changes
git add .

# Commit with descriptive message
git commit -m "Add feature: brief description of changes"
```

### 2. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 3. Create a Pull Request

1. Go to the original repository on GitHub
2. Click "New Pull Request"
3. Select your feature branch
4. Fill out the pull request template
5. Describe your changes and why they're needed

### Pull Request Guidelines

- **Title**: Clear, descriptive title
- **Description**: Explain what changes you made and why
- **Screenshots**: Include before/after screenshots for UI changes
- **Testing**: Describe how you tested your changes
- **Breaking Changes**: Note any breaking changes

## 🎨 Style Guidelines

### Python Code Style

- Follow [PEP 8](https://pep8.org/) style guidelines
- Use 4 spaces for indentation
- Use descriptive variable names
- Add docstrings to functions and classes
- Keep functions focused on single responsibilities

### Documentation

- Update README.md for new features
- Add comments for complex logic
- Include examples in docstrings
- Update help text for new command-line options

### Commit Messages

Use clear, descriptive commit messages:

```
feat: add support for new camera preset format
fix: resolve GPS geocoding timeout issue
docs: update installation instructions
style: format code according to PEP 8
```

### File Organization

- Keep camera presets in `camera_presets.py`
- Main logic in `exif_editor.py`
- Interactive interface in `easy_run.py`
- Dependencies in `requirements.txt`
- Setup scripts in repository root

## 📞 Getting Help

- 📧 **Issues**: [GitHub Issues](https://github.com/rahulrawatgujjar/exif-editor/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/rahulrawatgujjar/exif-editor/discussions)
- 📖 **Documentation**: Check the [Wiki](https://github.com/rahulrawatgujjar/exif-editor/wiki)

## 🙏 Recognition

Contributors will be recognized in:
- Repository contributors list
- Changelog for major releases
- Special mentions in release notes

Thank you for contributing to EXIF Editor! 🚀