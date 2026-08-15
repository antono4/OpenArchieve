import os
import io
import sys
import shutil
import zipfile
import tarfile
import gzip
import json
import random
import socket
import threading
import webbrowser
from datetime import datetime
from pathlib import Path

from flask import Flask, request, jsonify, send_file, abort, render_template


def resource_path(rel: str) -> Path:
    """Resolve a bundled resource path that works both in dev and when frozen by PyInstaller."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return Path(base) / rel


BASE_DIR = Path(os.environ.get("OPENARCHIEVE_HOME", Path.home() / ".openarchieve")).resolve()
WORK_DIR = BASE_DIR / "workspace_data"
UPLOAD_DIR = WORK_DIR / "uploads"
ARCHIVE_DIR = WORK_DIR / "archives"
EXTRACT_DIR = WORK_DIR / "extracted"

for d in (UPLOAD_DIR, ARCHIVE_DIR, EXTRACT_DIR):
    d.mkdir(parents=True, exist_ok=True)

app = Flask(
    __name__,
    template_folder=str(resource_path("templates")),
    static_folder=str(resource_path("static")),
)
app.config["MAX_CONTENT_LENGTH"] = 512 * 1024 * 1024  # 512 MB

ARCHIVE_FORMATS = {
    "zip": "ZIP archive (.zip)",
    "tar": "TAR archive (.tar)",
    "tar.gz": "Gzip-compressed TAR (.tar.gz)",
    "tar.bz2": "Bzip2-compressed TAR (.tar.bz2)",
    "tar.xz": "XZ-compressed TAR (.tar.xz)",
}


# Archive type detection (extension + magic bytes) for extract-anywhere support.
ARCHIVE_EXTS = (".zip", ".tar", ".tar.gz", ".tgz", ".tar.bz2", ".tbz2", ".tar.xz", ".txz", ".gz", ".bz2", ".xz")

_ZIP_MAGIC = b"PK\x03\x04"
_GZIP_MAGIC = b"\x1f\x8b"


def detect_archive_type(path: Path) -> str:
    """Return one of: zip, tar, tar.gz, tar.bz2, tar.xz, gzip, bz2, xz, or '' if unrecognized."""
    name = path.name.lower()
    try:
        with open(path, "rb") as f:
            magic = f.read(6)
    except OSError:
        return ""
    is_tar = False
    try:
        is_tar = tarfile.is_tarfile(path)
    except Exception:
        is_tar = False
    if name.endswith(".zip") or magic.startswith(_ZIP_MAGIC):
        return "zip"
    if name.endswith((".tar.gz", ".tgz")):
        return "tar.gz"
    if name.endswith(".tar.bz2") or name.endswith(".tbz2"):
        return "tar.bz2"
    if name.endswith(".tar.xz") or name.endswith(".txz"):
        return "tar.xz"
    if name.endswith(".tar") or is_tar:
        return "tar.gz" if magic.startswith(_GZIP_MAGIC) else ("tar.bz2" if magic.startswith(b"BZh") else ("tar.xz" if magic.startswith(b"\xfd7zXZ") else "tar"))
    if name.endswith(".gz") or magic.startswith(_GZIP_MAGIC):
        return "gzip"
    if name.endswith(".bz2") or magic.startswith(b"BZh"):
        return "bz2"
    if name.endswith(".xz") or magic.startswith(b"\xfd7zXZ"):
        return "xz"
    return ""


def _extract_any(target: Path, out_dir: Path, atype: str) -> None:
    """Extract an archive of the detected type into out_dir."""
    out_dir.mkdir(parents=True, exist_ok=True)
    if atype == "zip":
        with zipfile.ZipFile(target) as zf:
            zf.extractall(out_dir)
    elif atype in ("tar", "tar.gz", "tar.bz2", "tar.xz"):
        mode = {"tar": "r", "tar.gz": "r:gz", "tar.bz2": "r:bz2", "tar.xz": "r:xz"}[atype]
        with tarfile.open(target, mode) as tf:
            tf.extractall(out_dir)
    elif atype == "gzip":
        out_name = target.name[:-3] if target.name.lower().endswith(".gz") else target.name + ".out"
        with gzip.open(target, "rb") as src, open(out_dir / out_name, "wb") as dst:
            shutil.copyfileobj(src, dst)
    elif atype == "bz2":
        import bz2
        out_name = target.name[:-4] if target.name.lower().endswith(".bz2") else target.name + ".out"
        with bz2.open(target, "rb") as src, open(out_dir / out_name, "wb") as dst:
            shutil.copyfileobj(src, dst)
    elif atype == "xz":
        import lzma
        out_name = target.name[:-3] if target.name.lower().endswith(".xz") else target.name + ".out"
        with lzma.open(target, "rb") as src, open(out_dir / out_name, "wb") as dst:
            shutil.copyfileobj(src, dst)
    else:
        raise ValueError(f"Unsupported archive type: {atype or 'unknown'}")


def _safe_join(base: Path, rel: str) -> Path:
    """Join base with rel, ensuring the result stays within base (no path traversal)."""
    base = base.resolve()
    target = (base / rel).resolve()
    if base not in target.parents and target != base:
        abort(400, description="Invalid path")
    return target


def _relpath_from(base: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(base.resolve()).as_posix()
    except ValueError:
        return path.name


def _human_size(num: int) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(num) < 1024.0:
            return f"{num:.1f} {unit}"
        num /= 1024.0
    return f"{num:.1f} PB"


def _node_info(path: Path, base: Path):
    try:
        st = path.stat()
    except OSError:
        return None
    info = {
        "name": path.name if path != base else base.name,
        "path": _relpath_from(base, path),
        "is_dir": path.is_dir(),
        "size": st.st_size if path.is_file() else 0,
        "human_size": _human_size(st.st_size) if path.is_file() else "",
        "modified": datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
    }
    return info


def _list_dir(base: Path, rel: str = ""):
    target = _safe_join(base, rel)
    if not target.exists():
        return []
    items = []
    for child in sorted(target.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())):
        info = _node_info(child, base)
        if info:
            items.append(info)
    return items


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html", formats=ARCHIVE_FORMATS)


# ---------- File browser (uploads) ----------

@app.route("/api/files")
def api_files():
    rel = request.args.get("path", "")
    return jsonify({"items": _list_dir(UPLOAD_DIR, rel), "base": "uploads"})


@app.route("/api/files/tree")
def api_files_tree():
    """Return a flat listing for navigation breadcrumbs only."""
    rel = request.args.get("path", "")
    parts = [p for p in rel.split("/") if p]
    crumbs = [{"name": "uploads", "path": ""}]
    accum = ""
    for p in parts:
        accum = f"{accum}/{p}" if accum else p
        crumbs.append({"name": p, "path": accum})
    return jsonify({"breadcrumbs": crumbs, "items": _list_dir(UPLOAD_DIR, rel)})


# ---------- Upload ----------

@app.route("/api/upload", methods=["POST"])
def api_upload():
    rel = request.form.get("path", "")
    target_dir = _safe_join(UPLOAD_DIR, rel)
    if not target_dir.exists():
        target_dir.mkdir(parents=True, exist_ok=True)
    uploaded = []
    if "files" not in request.files:
        return jsonify({"error": "No files provided"}), 400
    for f in request.files.getlist("files"):
        if not f.filename:
            continue
        name = os.path.basename(f.filename)
        dest = target_dir / name
        f.save(str(dest))
        uploaded.append(name)
    return jsonify({"uploaded": uploaded, "count": len(uploaded)})


# ---------- Create folder ----------

@app.route("/api/mkdir", methods=["POST"])
def api_mkdir():
    data = request.get_json(force=True)
    rel = data.get("path", "")
    name = os.path.basename(data.get("name", ""))
    if not name:
        return jsonify({"error": "Invalid name"}), 400
    target = _safe_join(UPLOAD_DIR, f"{rel}/{name}" if rel else name)
    target.mkdir(parents=True, exist_ok=True)
    return jsonify({"ok": True, "path": _relpath_from(UPLOAD_DIR, target)})


# ---------- Delete ----------

@app.route("/api/delete", methods=["POST"])
def api_delete():
    data = request.get_json(force=True)
    rel = data.get("path", "")
    target = _safe_join(UPLOAD_DIR, rel)
    if not target.exists():
        return jsonify({"error": "Not found"}), 404
    if target.is_dir():
        shutil.rmtree(target)
    else:
        target.unlink()
    return jsonify({"ok": True})


# ---------- Create archive ----------

def _add_path_to_zip(zf, path, arcname):
    if path.is_dir():
        for child in sorted(path.iterdir()):
            _add_path_to_zip(zf, child, os.path.join(arcname, child.name))
    else:
        zf.write(path, arcname)


@app.route("/api/compress", methods=["POST"])
def api_compress():
    data = request.get_json(force=True)
    items = data.get("items", [])
    fmt = data.get("format", "zip")
    if fmt not in ARCHIVE_FORMATS:
        return jsonify({"error": "Unsupported format"}), 400
    if not items:
        return jsonify({"error": "No items selected"}), 400

    paths = []
    for rel in items:
        p = _safe_join(UPLOAD_DIR, rel)
        if p.exists():
            paths.append(p)
    if not paths:
        return jsonify({"error": "No valid items"}), 400

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    name_base = paths[0].stem if len(paths) == 1 else "archive"
    archive_name = f"{name_base}_{ts}"

    if fmt == "zip":
        out = ARCHIVE_DIR / f"{archive_name}.zip"
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
            for p in paths:
                arc = p.name
                _add_path_to_zip(zf, p, arc)
    else:
        mode = "w"
        ext = ".tar"
        if fmt == "tar.gz":
            mode = "w:gz"; ext = ".tar.gz"
        elif fmt == "tar.bz2":
            mode = "w:bz2"; ext = ".tar.bz2"
        elif fmt == "tar.xz":
            mode = "w:xz"; ext = ".tar.xz"
        out = ARCHIVE_DIR / f"{archive_name}{ext}"
        with tarfile.open(out, mode) as tf:
            for p in paths:
                tf.add(p, arcname=p.name)

    size = out.stat().st_size
    return jsonify({
        "ok": True,
        "archive": out.name,
        "path": out.name,
        "size": size,
        "human_size": _human_size(size),
    })


# ---------- List archives ----------

@app.route("/api/archives")
def api_archives():
    items = []
    for f in sorted(ARCHIVE_DIR.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
        if f.is_file():
            st = f.stat()
            items.append({
                "name": f.name,
                "path": f.name,
                "size": st.st_size,
                "human_size": _human_size(st.st_size),
                "modified": datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            })
    return jsonify({"items": items})


# ---------- Delete archive ----------

@app.route("/api/archives/delete", methods=["POST"])
def api_archives_delete():
    data = request.get_json(force=True)
    name = os.path.basename(data.get("path", ""))
    target = ARCHIVE_DIR / name
    if not target.exists():
        return jsonify({"error": "Not found"}), 404
    target.unlink()
    return jsonify({"ok": True})


# ---------- Download archive ----------

@app.route("/api/archives/download")
def api_archives_download():
    name = os.path.basename(request.args.get("path", ""))
    target = ARCHIVE_DIR / name
    if not target.exists():
        return jsonify({"error": "Not found"}), 404
    return send_file(str(target), as_attachment=True, download_name=name)


# ---------- List contents of an archive ----------

@app.route("/api/archives/contents")
def api_archives_contents():
    name = os.path.basename(request.args.get("path", ""))
    target = ARCHIVE_DIR / name
    if not target.exists():
        return jsonify({"error": "Not found"}), 404
    entries = []
    try:
        if name.endswith(".zip"):
            with zipfile.ZipFile(target) as zf:
                for zi in zf.infolist():
                    entries.append({
                        "name": zi.filename,
                        "is_dir": zi.is_dir(),
                        "size": zi.file_size,
                        "human_size": _human_size(zi.file_size),
                        "compressed": zi.compress_size,
                    })
        elif name.endswith((".tar", ".tar.gz", ".tar.bz2", ".tar.xz", ".tgz")):
            with tarfile.open(target) as tf:
                for m in tf.getmembers():
                    entries.append({
                        "name": m.name,
                        "is_dir": m.isdir(),
                        "size": m.size,
                        "human_size": _human_size(m.size),
                        "compressed": m.size,
                    })
        else:
            return jsonify({"error": "Unsupported archive type"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return jsonify({"items": entries})


# ---------- Extract archive (from the archives folder) ----------

@app.route("/api/extract", methods=["POST"])
def api_extract():
    data = request.get_json(force=True)
    name = os.path.basename(data.get("path", ""))
    sub = data.get("subdir", name + "_extracted")
    target = ARCHIVE_DIR / name
    if not target.exists():
        return jsonify({"error": "Not found"}), 404

    atype = data.get("type") or detect_archive_type(target)
    if not atype:
        return jsonify({"error": "Unsupported archive type"}), 400

    out_dir = _safe_join(EXTRACT_DIR, sub)
    try:
        _extract_any(target, out_dir, atype)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    files = _list_dir(out_dir, "")
    return jsonify({"ok": True, "subdir": sub, "type": atype, "items": files})


# ---------- Extract an uploaded archive (from the uploads folder) ----------

@app.route("/api/extract_uploads", methods=["POST"])
def api_extract_uploads():
    """Extract any archive file the user uploaded (zip/tar/gz/bz2/xz)."""
    data = request.get_json(force=True)
    rel = data.get("path", "")
    target = _safe_join(UPLOAD_DIR, rel)
    if not target.exists() or target.is_dir():
        return jsonify({"error": "File not found"}), 404

    atype = detect_archive_type(target)
    if not atype:
        return jsonify({"error": "Not a recognized archive (zip/tar/gz/bz2/xz)"}), 400

    sub = data.get("subdir") or (target.stem + "_extracted")
    out_dir = _safe_join(EXTRACT_DIR, sub)
    try:
        _extract_any(target, out_dir, atype)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    files = _list_dir(out_dir, "")
    return jsonify({"ok": True, "subdir": sub, "type": atype, "items": files})


# ---------- Detect archive type of an uploaded file ----------

@app.route("/api/archive_type")
def api_archive_type():
    rel = request.args.get("path", "")
    target = _safe_join(UPLOAD_DIR, rel)
    if not target.exists() or target.is_dir():
        return jsonify({"error": "File not found"}), 404
    return jsonify({"type": detect_archive_type(target), "is_archive": bool(detect_archive_type(target))})


# ---------- Download extracted file ----------

@app.route("/api/extracted/list")
def api_extracted_list():
    rel = request.args.get("path", "")
    return jsonify({"items": _list_dir(EXTRACT_DIR, rel)})


@app.route("/api/extracted/download")
def api_extracted_download():
    rel = request.args.get("path", "")
    target = _safe_join(EXTRACT_DIR, rel)
    if not target.exists() or target.is_dir():
        return jsonify({"error": "Not found"}), 404
    return send_file(str(target), as_attachment=True, download_name=target.name)


def find_free_port(preferred=12000):
    """Return a free TCP port, preferring the given one if available."""
    for port in (preferred, 0):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return s.getsockname()[1]
            except OSError:
                continue
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def launch_desktop(port=None, open_browser=True):
    port = port or find_free_port()
    url = f"http://127.0.0.1:{port}/"
    if open_browser:
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    print(f"OpenArchieve berjalan di {url}")
    app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False)


if __name__ == "__main__":
    if "--web" in sys.argv:
        app.run(host="0.0.0.0", port=12000, debug=True)
    else:
        no_browser = "--no-browser" in sys.argv
        launch_desktop(open_browser=not no_browser)
