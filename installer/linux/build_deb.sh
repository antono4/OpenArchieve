APP="OpenArchieve"
VERSION="1.0.0"
ARCH=$(dpkg --print-architecture 2>/dev/null || echo amd64)
BUILD_DIR="build_deb"
DEST="$BUILD_DIR/$APP"
PREFIX="/opt/$APP"

set -e

echo "=== Building .deb package for $APP $VERSION ($ARCH) ==="

# Rebuild the executable
echo "1/6 Building executable with PyInstaller..."
python3 -m PyInstaller OpenArchieve.spec --noconfirm >/dev/null 2>&1

# Clean previous build
rm -rf "$BUILD_DIR"
mkdir -p "$DEST$PREFIX" \
         "$DEST/usr/bin" \
         "$DEST/usr/share/applications" \
         "$DEST/usr/share/icons/hicolor/256x256/apps" \
         "$DEST/DEBIAN"
# Ensure no setgid bit is inherited (dpkg-deb rejects 2755)
chmod g-s "$BUILD_DIR" "$DEST" "$DEST/DEBIAN" 2>/dev/null || true

# Copy executable + icon + docs
echo "2/6 Copying files..."
cp dist/OpenArchieve "$DEST$PREFIX/OpenArchieve"
cp icon_256.png "$DEST$PREFIX/icon.png"
cp icon_256.png "$DEST/usr/share/icons/hicolor/256x256/apps/openarchieve.png"
cp README.md "$DEST$PREFIX/README.md"

# .desktop entry
cat > "$DEST/usr/share/applications/openarchieve.desktop" <<EOF
[Desktop Entry]
Name=OpenArchieve
Comment=File archiver (ZIP, TAR, GZ, BZ2, XZ)
Exec=$PREFIX/OpenArchieve --no-browser
Icon=openarchieve
Terminal=true
Type=Application
Categories=Utility;Archiving;
EOF

# Symlink in PATH
ln -s "$PREFIX/OpenArchieve" "$DEST/usr/bin/openarchieve"

# Control file
cat > "$DEST/DEBIAN/control" <<EOF
Package: $APP
Version: $VERSION
Section: utils
Priority: optional
Architecture: $ARCH
Depends:
Maintainer: OpenArchieve <openhands@all-hands.dev>
Description: File archiver like WinRAR/WinZip
 OpenArchieve is a web-based file archiver that runs as a local
 desktop app. It supports creating and extracting ZIP, TAR, TAR.GZ,
 TAR.BZ2, and TAR.XZ archives through a WinRAR-style dark UI.
Homepage: https://github.com/antono4/OpenArchieve
EOF

# Postinst: refresh desktop database
cat > "$DEST/DEBIAN/postinst" <<'EOF'
#!/bin/sh
set -e
update-desktop-database -q /usr/share/applications 2>/dev/null || true
gtk-update-icon-cache -q /usr/share/icons/hicolor 2>/dev/null || true
EOF
chmod 755 "$DEST/DEBIAN/postinst"

# Prerm
cat > "$DEST/DEBIAN/prerm" <<'EOF'
#!/bin/sh
set -e
pkill -f "OpenArchieve/OpenArchieve" 2>/dev/null || true
EOF
chmod 755 "$DEST/DEBIAN/prerm"

# Fix permissions
chmod 755 "$DEST$PREFIX/OpenArchieve"
chmod 644 "$DEST/usr/share/applications/openarchieve.desktop"
chmod 644 "$DEST/usr/share/icons/hicolor/256x256/apps/openarchieve.png"
find "$DEST/DEBIAN" -type d -exec chmod 0755 {} \;
find "$DEST/DEBIAN" -type f -exec chmod 0755 {} \;
chmod 0644 "$DEST/DEBIAN/control"
find "$DEST/usr" "$DEST$PREFIX" -type d -exec chmod 0755 {} \; 2>/dev/null || true

# Build the deb
echo "3/6 Building .deb..."
mkdir -p dist_installers
OUT="dist_installers/${APP}_${VERSION}_${ARCH}.deb"
dpkg-deb --build --root-owner-group "$DEST" "$OUT"

echo "4/6 Cleaning up..."
rm -rf "$BUILD_DIR"

echo "5/6 Verifying package..."
dpkg-deb --info "$OUT" | head -15

echo "6/6 Done!"
echo ""
echo "Installer created: $OUT"
echo "Install with:  sudo dpkg -i $OUT"
echo "Uninstall with: sudo dpkg -r $APP"
