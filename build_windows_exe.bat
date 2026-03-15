@echo off
setlocal

REM Build single-file Windows executable for EXIF Editor GUI
REM Run this on a Windows machine with Python installed.

echo.
echo === Building single-file EXIF Editor executable ===
echo.

where py >nul 2>&1
if errorlevel 1 (
    echo [FAIL] Python launcher 'py' not found.
    echo        Install Python 3.8+ and retry.
    exit /b 1
)

py -m pip install --upgrade pip
if errorlevel 1 exit /b 1

py -m pip install -r requirements.txt pyinstaller
if errorlevel 1 exit /b 1

py -m PyInstaller --noconfirm --clean --onefile --windowed --name ExifEditor easy_run.py
if errorlevel 1 (
    echo.
    echo [FAIL] Build failed.
    exit /b 1
)

echo.
echo [OK] Build complete.
echo      Executable: dist\ExifEditor.exe
echo      Share this single file with Windows users.
echo.

exit /b 0
