# Setup script for EXIF Editor - Windows PowerShell
# Equivalent of setup.sh for Windows users
#
# Usage:
#   .\setup.ps1
#
# If blocked by execution policy, run once as admin:
#   Set-ExecutionPolicy -Scope CurrentUser RemoteSigned

param()
$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "=== Setting up EXIF Editor with virtual environment ===" -ForegroundColor Cyan
Write-Host ""

# ---------------------------------------------------------------------------
# 1. Locate Python
# ---------------------------------------------------------------------------
$pythonCmd = $null
foreach ($candidate in @("python", "python3")) {
    try {
        $ver = & $candidate --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            $pythonCmd = $candidate
            break
        }
    } catch {}
}

if (-not $pythonCmd) {
    Write-Host "[FAIL] Python is not installed or not in PATH." -ForegroundColor Red
    Write-Host "       Download Python 3.8+ from https://python.org" -ForegroundColor Yellow
    Write-Host "       Make sure to check 'Add Python to PATH' during installation." -ForegroundColor Yellow
    exit 1
}

# ---------------------------------------------------------------------------
# 2. Check Python version >= 3.8
# ---------------------------------------------------------------------------
$versionStr = & $pythonCmd -c "import sys; print('{}.{}'.format(*sys.version_info[:2]))"
$parts = $versionStr.Trim().Split(".")
$major  = [int]$parts[0]
$minor  = [int]$parts[1]

if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 8)) {
    Write-Host "[FAIL] Python $versionStr detected. Python 3.8 or higher is required." -ForegroundColor Red
    exit 1
}

Write-Host "[OK]  Python $versionStr found" -ForegroundColor Green

# ---------------------------------------------------------------------------
# 3. Handle existing virtual environment
# ---------------------------------------------------------------------------
if (Test-Path "venv") {
    Write-Host ""
    Write-Host "[WARN] Virtual environment already exists." -ForegroundColor Yellow
    $answer = Read-Host "       Remove and recreate? (y/N)"

    if ($answer -match "^[Yy]$") {
        Write-Host "       Removing existing virtual environment..." -ForegroundColor Yellow
        Remove-Item -Recurse -Force "venv"
    } else {
        Write-Host "       Using existing virtual environment..." -ForegroundColor Cyan
        Write-Host "       Checking dependencies..."

        $venvPython = Join-Path $PSScriptRoot "venv\Scripts\python.exe"
        $check = & $venvPython -c "import PIL, piexif" 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Host "       Installing/updating dependencies..." -ForegroundColor Cyan
            & $venvPython -m pip install --upgrade pip | Out-Null
            & $venvPython -m pip install -r requirements.txt
        } else {
            Write-Host "[OK]  Dependencies already installed" -ForegroundColor Green
        }

        Write-Host ""
        Write-Host "=== Setup complete! ===" -ForegroundColor Green
        Write-Host ""
        Write-Host "To use the interactive EXIF editor:" -ForegroundColor Cyan
        Write-Host "  .\venv\Scripts\Activate.ps1"
        Write-Host "  python easy_run.py"
        Write-Host ""
        Write-Host "Or run directly without manual activation:"
        Write-Host "  python test_setup.py    # verify everything works"
        Write-Host "  python easy_run.py      # interactive mode"
        exit 0
    }
}

# ---------------------------------------------------------------------------
# 4. Create virtual environment
# ---------------------------------------------------------------------------
Write-Host ""
Write-Host "      Creating virtual environment..." -ForegroundColor Cyan
& $pythonCmd -m venv venv

$venvPython = Join-Path $PSScriptRoot "venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Host "[FAIL] Virtual environment creation failed." -ForegroundColor Red
    exit 1
}
Write-Host "[OK]  Virtual environment created" -ForegroundColor Green

# ---------------------------------------------------------------------------
# 5. Upgrade pip
# ---------------------------------------------------------------------------
Write-Host "      Upgrading pip..." -ForegroundColor Cyan
& $venvPython -m pip install --upgrade pip | Out-Null
Write-Host "[OK]  pip upgraded" -ForegroundColor Green

# ---------------------------------------------------------------------------
# 6. Install dependencies
# ---------------------------------------------------------------------------
Write-Host "      Installing dependencies..." -ForegroundColor Cyan
& $venvPython -m pip install -r requirements.txt
Write-Host "[OK]  Dependencies installed" -ForegroundColor Green

# ---------------------------------------------------------------------------
# 7. Verify imports
# ---------------------------------------------------------------------------
Write-Host ""
Write-Host "      Testing installation..." -ForegroundColor Cyan
$importCheck = & $venvPython -c "import PIL, piexif; print('imports OK')" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK]  All dependencies verified" -ForegroundColor Green
} else {
    Write-Host "[FAIL] Import check failed: $importCheck" -ForegroundColor Red
    exit 1
}

# ---------------------------------------------------------------------------
# 8. Done
# ---------------------------------------------------------------------------
Write-Host ""
Write-Host "=== Setup completed successfully! ===" -ForegroundColor Green
Write-Host ""
Write-Host "Quick start:" -ForegroundColor Cyan
Write-Host "  python test_setup.py   # run full verification"
Write-Host "  python easy_run.py     # interactive mode"
Write-Host ""
Write-Host "Or activate the virtual environment manually first:"
Write-Host "  .\venv\Scripts\Activate.ps1"
Write-Host "  python exif_editor.py --help"
Write-Host ""
