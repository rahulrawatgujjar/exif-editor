#!/usr/bin/env python3
"""
Python launcher that automatically uses the virtual environment
"""
import os
import sys
import subprocess

# Get the directory of this script
script_dir = os.path.dirname(os.path.abspath(__file__))
venv_python = os.path.join(script_dir, 'venv', 'bin', 'python3')

# Check if virtual environment exists
if os.path.exists(venv_python):
    # Use virtual environment Python
    os.execv(venv_python, [venv_python] + sys.argv[1:])
else:
    # Fall back to system Python
    print("Warning: Virtual environment not found, using system Python")
    os.execv(sys.executable, [sys.executable] + sys.argv[1:])