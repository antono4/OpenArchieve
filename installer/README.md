# OpenArchieve — Installer Files

Installer untuk semua OS: **Linux** (.deb, .rpm, .run), **Windows** (.exe), **macOS** (.dmg, .pkg).

## Struktur
```
installer/
├── icon.svg                 Ikon sumber (vektor)
├── make_icon.py             Generate ikon PNG + ICO (16–256px)
├── linux/
│   ├── build_deb.sh         Build .deb (Debian/Ubuntu/Mint)
│   ├── build_rpm.sh         Build .rpm (Fedora/RHEL/openSUSE)
│   ├── build_selfextract.sh Build .run self-extracting (semua distro)
│   └── openarchieve.spec    Spec untuk rpmbuild
├── windows/
│   ├── openarchieve.iss     Skrip Inno Setup
│   └── build_windows_installer.bat   Build otomatis (Windows)
└── macos/
    └── build_macos.sh       Build .dmg + .pkg + .app bundle
build_all.sh                 Build semua installer untuk OS saat ini
```

## Build semua installer (Linux/macOS)
```bash
./build_all.sh
```
Hasil di `dist_installers/`.

## Per-OS

### Linux .deb (Debian/Ubuntu/Mint)
```bash
./installer/linux/build_deb.sh
# Output: dist_installers/OpenArchieve_1.0.0_amd64.deb
# Install:  sudo dpkg -i dist_installers/OpenArchieve_1.0.0_amd64.deb
# Hapus:    sudo dpkg -r OpenArchieve
```

### Linux .rpm (Fedora/RHEL/openSUSE)
Butuh `rpmbuild` atau `fpm`:
```bash
# Install tool (pilih satu):
sudo dnf install rpm-build      # Fedora/RHEL
gem install fpm                  # fpm (semua distro)
./installer/linux/build_rpm.sh
# Install:  sudo rpm -i dist_installers/openarchieve-*.rpm
# Hapus:    sudo rpm -e openarchieve
```

### Linux .run (self-extracting, semua distro)
Tidak butuh dpkg/rpm. Bekerja di Linux & macOS:
```bash
./installer/linux/build_selfextract.sh
# Output: dist_installers/OpenArchieve-1.0.0-installer.run
# Install:  sudo ./dist_installers/OpenArchieve-1.0.0-installer.run
# Hapus:    sudo rm -rf /opt/OpenArchieve /usr/bin/openarchieve /usr/share/applications/openarchieve.desktop
```

### Windows .exe (installer GUI)
Build **di Windows**. Butuh [Inno Setup 6](https://jrsoftware.org/isdl.php):
```bat
installer\windows\build_windows_installer.bat
```
Output: `dist_installers\OpenArchieve-Setup-1.0.0.exe`
Install: klik dua kali .exe → ikuti wizard.

### macOS .dmg / .pkg
Build **di macOS**:
```bash
./installer/macos/build_macos.sh
# Install .dmg: klik dua kali, drag OpenArchieve ke Applications
# Install .pkg: klik dua kali, ikuti wizard
# Hapus: drag OpenArchieve.app dari Applications ke Trash
```

## Setelah install
- **Linux**: buka dari menu aplikasi "OpenArchieve", atau terminal `openarchieve --no-browser`
- **Windows**: Start Menu → OpenArchieve, atau klik dua-klik shortcut desktop
- **macOS**: Launchpad → OpenArchieve, atau Applications folder

Browser terbuka otomatis. Data arsip di `~/.openarchieve/workspace_data/`
(ubah via env `OPENARCHIEVE_HOME`).

## Catatan
- Build native: .deb/.rpm/.run harus dibuat di Linux; .exe di Windows; .dmg/.pkg di macOS.
  (PyInstaller tidak cross-compile.)
- .deb & .run sudah diuji end-to-end di build ini.
