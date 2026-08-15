#!/usr/bin/env bash
# Build script for OpenArchieve (Linux/macOS)
# Produces a single standalone executable in dist/
set -e

echo "=== OpenArchieve - Standalone Executable Builder ==="

pip install -r requirements.txt

python -m PyInstaller OpenArchieve.spec --noconfirm --clean

echo ""
echo "=== Build selesai! ==="
echo "Output: dist/OpenArchieve"
echo ""
echo "Jalankan dengan: ./dist/OpenArchieve"
echo "Browser akan terbuka otomatis."
