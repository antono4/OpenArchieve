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
