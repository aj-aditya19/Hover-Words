@echo off
REM Builds Hover Dictionary into a single standalone .exe with PyInstaller.
REM Run this from the project folder (where main.py lives) on Windows,
REM with your virtualenv/dependencies already installed.
REM
REM Before running: make sure vendor\tesseract\ exists and contains a
REM portable Tesseract build (tesseract.exe + tessdata folder + DLLs).
REM See README.md -> "Building the installer" section for where to get one.

pip install pyinstaller

pyinstaller ^
    --name HoverDictionary ^
    --onefile ^
    --noconsole ^
    --add-data "vendor\tesseract;vendor\tesseract" ^
    main.py

echo.
echo Build finished. Find the exe at: dist\HoverDictionary.exe
