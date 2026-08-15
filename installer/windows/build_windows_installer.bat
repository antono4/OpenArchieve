@echo off
REM ============================================================
REM  OpenArchieve Windows installer builder
REM  Produces: dist_installers\OpenArchieve-Setup-1.0.0.exe
REM  Requirements: Python, Inno Setup 6 (https://jrsoftware.org/isdl.php)
REM ============================================================

echo === OpenArchieve - Windows Installer Builder ===

REM 1) Install deps + build executable
python -m pip install -r requirements.txt
python -m PyInstaller OpenArchieve.spec --noconfirm --clean

REM 2) Build installer with Inno Setup
set ISCC="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if not exist %ISCC% set ISCC="C:\Program Files\Inno Setup 6\ISCC.exe"
if not exist %ISCC% (
    echo ERROR: Inno Setup 6 not found. Install from https://jrsoftware.org/isdl.php
    pause
    exit /b 1
)
%ISCC% installer\windows\openarchieve.iss

echo.
echo === Done! ===
echo Installer: dist_installers\OpenArchieve-Setup-1.0.0.exe
echo Install: double-click the .exe and follow the wizard.
pause
