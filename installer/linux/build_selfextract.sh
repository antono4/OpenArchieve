#!/usr/bin/env bash
# Build a self-extracting installer for Linux/macOS that needs no dpkg/rpm.
# Produces a single .run file: dist_installers/OpenArchieve-1.0.0-installer.run
# Install later with:  sudo ./OpenArchieve-1.0.0-installer.run
#
# Method: tar the executable + assets, append a payload marker + installer
#         script, and prepend a shebang. Works on any POSIX system with tar.

set -e
APP="OpenArchieve"
VERSION="1.0.0"
PREFIX="/opt/$APP"
ARCH=$(uname -m)

echo "=== Building self-extracting installer for $APP $VERSION ($ARCH) ==="

echo "1/4 Building executable with PyInstaller..."
python3 -m PyInstaller OpenArchieve.spec --noconfirm >/dev/null 2>&1

STAGING="build_selfx"
rm -rf "$STAGING"
mkdir -p "$STAGING/payload"

# Collect files into payload mirroring install layout
mkdir -p "$STAGING/payload/$PREFIX" \
         "$STAGING/payload/usr/bin" \
         "$STAGING/payload/usr/share/applications" \
         "$STAGING/payload/usr/share/icons/hicolor/256x256/apps"

cp dist/OpenArchieve "$STAGING/payload/$PREFIX/OpenArchieve"
cp icon_256.png "$STAGING/payload/$PREFIX/icon.png"
cp README.md "$STAGING/payload/$PREFIX/README.md"
cp icon_256.png "$STAGING/payload/usr/share/icons/hicolor/256x256/apps/openarchieve.png"
ln -s "$PREFIX/OpenArchieve" "$STAGING/payload/usr/bin/openarchieve"

cat > "$STAGING/payload/usr/share/applications/openarchieve.desktop" <<EOF
[Desktop Entry]
Name=OpenArchieve
Comment=File archiver (ZIP, TAR, GZ, BZ2, XZ)
Exec=$PREFIX/OpenArchieve --no-browser
Icon=openarchieve
Terminal=true
Type=Application
Categories=Utility;Archiving;
EOF

chmod 755 "$STAGING/payload/$PREFIX/OpenArchieve"

echo "2/4 Creating payload tarball..."
tar -C "$STAGING/payload" -czf "$STAGING/payload.tar.gz" .

echo "3/4 Writing installer script..."
# The installer reads the payload appended after a marker line from THIS file.
cat > "$STAGING/installer.sh" <<'SCRIPT_EOF'
#!/usr/bin/env bash
# Self-extracting installer for OpenArchieve
set -e
PREFIX="/opt/OpenArchieve"
BIN_LINK="/usr/bin/openarchieve"
MARKER="__PAYLOAD_BELOW__"

if [ "$(id -u)" -ne 0 ]; then
    echo "Please run as root:  sudo $0"
    exit 1
fi

SELF="$0"
LINE=$(grep -an "^$MARKER$" "$SELF" | head -1 | cut -d: -f1)
if [ -z "$LINE" ]; then
    echo "ERROR: payload marker not found. Corrupt installer?" >&2
    exit 1
fi
TMPDIR=$(mktemp -d /tmp/openarchieve.XXXXXX)
trap 'rm -rf "$TMPDIR"' EXIT
PAYLOAD="$TMPDIR/payload.tar.gz"
tail -n +"$((LINE + 1))" "$SELF" > "$PAYLOAD"

echo "Installing OpenArchieve to $PREFIX ..."
mkdir -p "$TMPDIR/root"
tar -C "$TMPDIR/root" -xzf "$PAYLOAD"
cp -R "$TMPDIR/root/." /

chmod 755 "$PREFIX/OpenArchieve" 2>/dev/null || true
ln -sf "$PREFIX/OpenArchieve" "$BIN_LINK" 2>/dev/null || true
update-desktop-database -q /usr/share/applications 2>/dev/null || true
gtk-update-icon-cache -q /usr/share/icons/hicolor 2>/dev/null || true

echo "Done! OpenArchieve installed."
echo "  Run from menu: OpenArchieve"
echo "  Run from terminal: openarchieve --no-browser"
echo "  Uninstall: sudo rm -rf $PREFIX $BIN_LINK /usr/share/applications/openarchieve.desktop"
exit 0
__PAYLOAD_BELOW__
SCRIPT_EOF
chmod 755 "$STAGING/installer.sh"

echo "4/4 Assembling .run file..."
mkdir -p dist_installers
OUT="dist_installers/${APP}-${VERSION}-installer.run"
cat "$STAGING/installer.sh" "$STAGING/payload.tar.gz" > "$OUT"
chmod 755 "$OUT"
rm -rf "$STAGING"

echo ""
echo "Installer created: $OUT ($(ls -lh "$OUT" | awk '{print $5}'))"
echo "Install with:  sudo $OUT"
