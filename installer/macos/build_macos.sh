#!/usr/bin/env bash
# Build a macOS .app bundle + .dmg installer for OpenArchieve.
# Run on macOS. Produces:
#   dist_installers/OpenArchieve-1.0.0.dmg
#   dist_installers/OpenArchieve-1.0.0.pkg
# Requirements: Python, PyInstaller (from requirements.txt), hdiutil (built-in), pkgbuild (built-in).

set -e
APP="OpenArchieve"
VERSION="1.0.0"
APPDIR="build_mac/$APP.app"
CONTENTS="$APPDIR/Contents"
MACOS="$CONTENTS/MacOS"
RESOURCES="$CONTENTS/Resources"

echo "=== Building macOS .app + .dmg for $APP $VERSION ==="

# 1) Build the executable (must be built ON macOS for a native binary)
echo "1/5 Building executable with PyInstaller..."
python3 -m PyInstaller OpenArchieve.spec --noconfirm >/dev/null 2>&1

# 2) Assemble .app bundle
echo "2/5 Assembling .app bundle..."
rm -rf build_mac
mkdir -p "$MACOS" "$RESOURCES"
cp dist/OpenArchieve "$MACOS/OpenArchieve"
cp icon_256.png "$RESOURCES/icon.png"
cp README.md "$RESOURCES/README.md"

# Info.plist
cat > "$CONTENTS/Info.plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>            <string>OpenArchieve</string>
    <key>CFBundleDisplayName</key>     <string>OpenArchieve</string>
    <key>CFBundleIdentifier</key>      <string>dev.all-hands.openarchieve</string>
    <key>CFBundleVersion</key>         <string>$VERSION</string>
    <key>CFBundleShortVersionString</key> <string>$VERSION</string>
    <key>CFBundlePackageType</key>     <string>APPL</string>
    <key>CFBundleExecutable</key>      <string>OpenArchieve</string>
    <key>CFBundleIconFile</key>        <string>icon</string>
    <key>LSMinimumSystemVersion</key>  <string>10.13</string>
    <key>NSHighResolutionCapable</key>  <true/>
    <key>LSUIElement</key>             <false/>
</dict>
</plist>
EOF

# 3) Create .dmg (drag-to-Applications)
echo "3/5 Building .dmg..."
mkdir -p dist_installers
DMG="dist_installers/${APP}-${VERSION}.dmg"
STAGING="build_mac/dmg_staging"
mkdir -p "$STAGING"
cp -R "$APPDIR" "$STAGING/"
ln -s /Applications "$STAGING/Applications"
hdiutil create -volname "$APP" -srcfolder "$STAGING" -ov -format UDZO "$DMG"
rm -rf "$STAGING"

# 4) Create .pkg (system installer)
echo "4/5 Building .pkg..."
PKG="dist_installers/${APP}-${VERSION}.pkg"
pkgbuild --root "$APPDIR" --identifier dev.all-hands.openarchieve --version "$VERSION" "$PKG" || \
    echo "(pkgbuild needs root install; .dmg is the recommended macOS installer)"

# 5) Cleanup
echo "5/5 Done!"
rm -rf build_mac

echo ""
ls -lh dist_installers/*.dmg dist_installers/*.pkg 2>/dev/null
echo ""
echo "Install (.dmg): double-click, drag OpenArchieve to Applications"
echo "Install (.pkg): double-click and follow installer wizard"
echo "Uninstall: drag OpenArchieve.app from Applications to Trash"
