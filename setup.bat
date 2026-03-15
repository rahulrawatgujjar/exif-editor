@echo off
REM Setup launcher for EXIF Editor on Windows Command Prompt
REM Delegates to setup.ps1 via PowerShell
REM
REM Usage:
REM   setup.bat

echo.
echo === EXIF Editor Windows Setup ===
echo.

REM Check PowerShell availability
where powershell >nul 2>&1
if errorlevel 1 (
    echo [FAIL] PowerShell is not available on this system.
    echo        Please install PowerShell or run setup.ps1 manually.
    exit /b 1
)

echo Launching PowerShell setup script...
echo.

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup.ps1"
set EXIT_CODE=%ERRORLEVEL%

if not "%EXIT_CODE%"=="0" (
    echo.
    echo [FAIL] Setup failed with exit code %EXIT_CODE%.
    echo        Review the messages above and fix any errors.
    exit /b %EXIT_CODE%
)

exit /b 0
