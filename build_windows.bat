@echo off
REM ============================================================
REM  Build script for OpenArchieve.exe (Windows)
REM  Run this on a Windows machine with Python installed.
REM ============================================================

echo === OpenArchieve - Windows EXE Builder ===

REM Install dependencies
python -m pip install -r requirements.txt

REM Build the executable (single file)
python -m PyInstaller OpenArchieve.spec --noconfirm --clean

echo.
echo === Build selesai! ===
echo Output: dist\OpenArchieve.exe
echo.
echo Jalankan dengan: dist\OpenArchieve.exe
echo Browser akan terbuka otomatis.
pause
