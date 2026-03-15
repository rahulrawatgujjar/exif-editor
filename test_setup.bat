@echo off
setlocal

REM Cross-platform setup check wrapper for Windows CMD
python test_setup.py
set EXIT_CODE=%ERRORLEVEL%

if not "%EXIT_CODE%"=="0" (
  echo.
  echo Setup verification failed with exit code %EXIT_CODE%.
  exit /b %EXIT_CODE%
)

echo.
echo Setup verification completed successfully.
exit /b 0
