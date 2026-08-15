#!/usr/bin/env bash
# Build an RPM package for OpenArchieve.
# Requires: rpm-build (rpmbuild) OR fpm. Install one if missing.
# Run on a Linux distro with RPM tooling (Fedora, RHEL, openSUSE, etc.).

set -e
APP="OpenArchieve"
VERSION="1.0.0"
ARCH=$(uname -m)

echo "=== Building .rpm package for $APP $VERSION ($ARCH) ==="

# 1) Build the executable
echo "1/3 Building executable with PyInstaller..."
python3 -m PyInstaller OpenArchieve.spec --noconfirm >/dev/null 2>&1

mkdir -p dist_installers

# 2) Try fpm first (easiest cross-distro), then rpmbuild
if command -v fpm >/dev/null 2>&1; then
    echo "2/3 Building with fpm..."
    fpm -s dir -t rpm \
        -n openarchieve -v "$VERSION" --iteration 1 \
        -a "$ARCH" \
        -m "OpenArchieve <openhands@all-hands.dev>" \
        --url https://github.com/antono4/OpenArchieve \
        --description "File archiver like WinRAR/WinZip" \
        --license MIT \
        -p dist_installers/ \
        dist/OpenArchieve=/opt/OpenArchieve/OpenArchieve \
        icon_256.png=/opt/OpenArchieve/icon.png \
        README.md=/opt/OpenArchieve/README.md \
        icon_256.png=/usr/share/icons/hicolor/256x256/apps/openarchieve.png
    # symlink + desktop entry
    mkdir -p /tmp/oa_rpm/usr/bin /tmp/oa_rpm/usr/share/applications
    ln -sf /opt/OpenArchieve/OpenArchieve /tmp/oa_rpm/usr/bin/openarchieve
    cat > /tmp/oa_rpm/usr/share/applications/openarchieve.desktop <<EOF
[Desktop Entry]
Name=OpenArchieve
Comment=File archiver (ZIP, TAR, GZ, BZ2, XZ)
Exec=/opt/OpenArchieve/OpenArchieve --no-browser
Icon=openarchieve
Terminal=true
Type=Application
Categories=Utility;Archiving;
EOF
    fpm -s dir -t rpm -n openarchieve -v "$VERSION" --iteration 1 -a "$ARCH" \
        -p dist_installers/ /tmp/oa_rpm/=/ || true
    rm -rf /tmp/oa_rpm
elif command -v rpmbuild >/dev/null 2>&1; then
    echo "2/3 Building with rpmbuild..."
    ROOT=$(pwd)/build_rpm
    rm -rf "$ROOT"
    rpmbuild --define "_topdir $ROOT" -bb installer/linux/openarchieve.spec
    find "$ROOT/RPMS" -name "*.rpm" -exec cp {} dist_installers/ \;
    rm -rf "$ROOT"
else
    echo "ERROR: Neither 'fpm' nor 'rpmbuild' is installed." >&2
    echo "Install with one of:" >&2
    echo "  sudo dnf install rpm-build   # Fedora/RHEL" >&2
    echo "  sudo zypper install rpm-build # openSUSE" >&2
    echo "  gem install fpm               # fpm (any distro)" >&2
    exit 1
fi

echo "3/3 Done!"
echo ""
ls -lh dist_installers/*.rpm 2>/dev/null
echo ""
echo "Install with:  sudo rpm -i dist_installers/openarchieve-*.rpm"
echo "Uninstall with: sudo rpm -e openarchieve"
