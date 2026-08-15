# OpenArchieve

Aplikasi kompresor file seperti WinRAR/WinZip — berbasis web yang dibungkus menjadi aplikasi desktop standalone (exe).

## Fitur
- File Manager: unggah (klik & drag-drop), buat folder, navigasi, hapus
- Kompres ke 5 format: ZIP, TAR, TAR.GZ, TAR.BZ2, TAR.XZ
- Daftar arsip: download, ekstrak, hapus
- Hasil ekstrak: navigasi folder & download file individual
- UI dark theme ala WinRAR
- Proteksi path traversal

## Menjalankan sebagai aplikasi desktop
Setelah build, jalankan executable:
- **Linux/macOS:** `./dist/OpenArchieve`
- **Windows:** `dist\OpenArchieve.exe`

Browser akan terbuka otomatis. Data disimpan di `~/.openarchieve/workspace_data/`.
Atur lokasi lain dengan env `OPENARCHIEVE_HOME`.

## Build executable

### Linux / macOS
```bash
./build.sh
```

### Windows (menghasilkan .exe asli)
Jalankan di mesin Windows:
```bat
build_windows.bat
```
Output: `dist\OpenArchieve.exe`

> Catatan: file `.exe` Windows hanya bisa dibuat di Windows. Untuk distribusi Windows, build di Windows.
> Di Linux hasilnya adalah executable ELF (tidak butuh Python terinstall).

## Installer (semua OS)
Lihat [`installer/README.md`](installer/README.md). Ringkasan:

| OS | Format | Cara build | Install |
|----|--------|------------|---------|
| Linux (Debian/Ubuntu) | `.deb` | `./installer/linux/build_deb.sh` | `sudo dpkg -i dist_installers/OpenArchieve_1.0.0_amd64.deb` |
| Linux (Fedora/RHEL) | `.rpm` | `./installer/linux/build_rpm.sh` | `sudo rpm -i dist_installers/openarchieve-*.rpm` |
| Linux (semua) | `.run` | `./installer/linux/build_selfextract.sh` | `sudo ./dist_installers/OpenArchieve-1.0.0-installer.run` |
| Windows | `.exe` | `installer\windows\build_windows_installer.bat` (di Windows) | klik dua-klik |
| macOS | `.dmg`/`.pkg` | `./installer/macos/build_macos.sh` (di macOS) | klik dua-klik |

Build semua installer untuk OS saat ini:
```bash
./build_all.sh
```
Hasil di `dist_installers/`.

> Catatan: installer native harus dibuat di OS targetnya (.deb/.rpm/.run di Linux, .exe di Windows, .dmg/.pkg di macOS).

## Menjalankan mode web (development)
```bash
python app.py --web
```
Server berjalan di `http://0.0.0.0:12000` dengan debug aktif.

## Struktur
```
app.py              Backend Flask + launcher desktop
templates/          UI HTML
static/             CSS & JS
OpenArchieve.spec   Konfigurasi PyInstaller
build.sh            Build Linux/macOS
build_windows.bat   Build Windows
```
