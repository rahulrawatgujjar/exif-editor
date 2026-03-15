#!/usr/bin/env python3
"""
Python launcher that automatically uses the virtual environment
"""
import os
import sys


def find_venv_python(script_dir: str) -> str | None:
    """Return the project venv Python path for Windows/Unix, if present."""
    candidates = [
        os.path.join(script_dir, "venv", "Scripts", "python.exe"),  # Windows
        os.path.join(script_dir, "venv", "Scripts", "python"),      # Windows/MSYS
        os.path.join(script_dir, "venv", "bin", "python3"),         # Unix
        os.path.join(script_dir, "venv", "bin", "python"),          # Unix fallback
    ]
    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate
    return None

# Get the directory of this script
script_dir = os.path.dirname(os.path.abspath(__file__))
venv_python = find_venv_python(script_dir)

# Check if virtual environment exists
if venv_python:
    # Use virtual environment Python
    os.execv(venv_python, [venv_python] + sys.argv[1:])
else:
    # Fall back to system Python
    print("Warning: Virtual environment not found, using system Python")
    os.execv(sys.executable, [sys.executable] + sys.argv[1:])