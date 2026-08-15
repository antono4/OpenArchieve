#!/usr/bin/env bash
# Build all available installers for the current OS.
# - On Linux:  .deb, .rpm (if tooling present), self-extracting .run
# - On macOS:   .dmg + .pkg
# - On Windows: Inno Setup .exe (requires ISCC)  -- use build_windows_installer.bat
set -e

OS="$(uname -s)"
echo "=== OpenArchieve build-all on $OS ==="

# Ensure icons exist
[ -f icon_256.png ] || python3 installer/make_icon.py
[ -f icon_256.ico ] || python3 installer/make_icon.py 2>/dev/null || true

# Build the base executable once
echo "--- Building executable ---"
python3 -m PyInstaller OpenArchieve.spec --noconfirm >/dev/null 2>&1

case "$OS" in
  Linux)
    echo "--- Linux: .deb ---"
    bash installer/linux/build_deb.sh || echo "(deb build failed)"
    echo "--- Linux: .rpm ---"
    bash installer/linux/build_rpm.sh || echo "(rpm build skipped -- needs fpm/rpmbuild)"
    echo "--- Linux: self-extracting .run ---"
    bash installer/linux/build_selfextract.sh || echo "(run build failed)"
    ;;
  Darwin)
    echo "--- macOS: .dmg + .pkg ---"
    bash installer/macos/build_macos.sh || echo "(macOS build failed)"
    ;;
  *)
    echo "Unknown OS $OS. On Windows use installer\\windows\\build_windows_installer.bat"
    ;;
esac

echo ""
echo "=== All installers in dist_installers/ ==="
ls -lh dist_installers/ 2>/dev/null || echo "(no installers produced)"
