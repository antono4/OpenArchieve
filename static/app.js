const API = (p) => `/api/${p}`;
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));

let currentPath = "";
let currentTab = "files";
let selected = new Set();

const ICONS = {
  folder: "📁",
  zip: "🗜️", tar: "🗜️", gz: "🗜️",
  txt: "📄", pdf: "📕", doc: "📘",
  img: "🖼️", png: "🖼️", jpg: "🖼️", jpeg: "🖼️", gif: "🖼️",
  audio: "🎵", mp3: "🎵", wav: "🎵",
  video: "🎬", mp4: "🎬", mov: "🎬",
  code: "📝", py: "📝", js: "📝", html: "📝", css: "📝",
  default: "📄",
};

function iconFor(name, isDir) {
  if (isDir) return ICONS.folder;
  const ext = name.split(".").pop().toLowerCase();
  if (["zip"].includes(ext)) return ICONS.zip;
  if (["tar", "gz", "bz2", "xz", "tgz"].includes(ext)) return ICONS.tar;
  if (["png", "jpg", "jpeg", "gif", "bmp", "svg", "webp"].includes(ext)) return ICONS.img;
  if (["mp3", "wav", "ogg", "flac"].includes(ext)) return ICONS.audio;
  if (["mp4", "mov", "avi", "mkv", "webm"].includes(ext)) return ICONS.video;
  if (["txt", "md", "log"].includes(ext)) return ICONS.txt;
  if (["pdf"].includes(ext)) return ICONS.pdf;
  if (["doc", "docx"].includes(ext)) return ICONS.doc;
  if (["py", "js", "html", "css", "json", "java", "c", "cpp", "sh", "go", "rs"].includes(ext)) return ICONS.code;
  return ICONS.default;
}

function toast(msg, type = "ok") {
  const wrap = $("#toastWrap");
  const t = document.createElement("div");
  t.className = `toast ${type === "err" ? "err" : type === "info" ? "info" : ""}`;
  t.textContent = msg;
  wrap.appendChild(t);
  setTimeout(() => { t.style.opacity = "0"; setTimeout(() => t.remove(), 300); }, 3200);
}

async function api(path, opts = {}) {
  const res = await fetch(API(path), opts);
  let data = {};
  try { data = await res.json(); } catch (e) {}
  if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`);
  return data;
}

// ---------- Tabs ----------
function setTab(tab) {
  currentTab = tab;
  $$(".tab").forEach(t => t.classList.toggle("active", t.dataset.tab === tab));
  $$(".side-btn").forEach(b => b.classList.toggle("active", b.dataset.tab === tab));
  selected.clear();
  if (tab === "files") { currentPath = ""; loadFiles(); }
  else if (tab === "archives") loadArchives();
  else if (tab === "extracted") { currentPath = ""; loadExtracted(); }
  updateActions();
}

// ---------- Files tab ----------
async function loadFiles() {
  try {
    const data = await api(`files/tree?path=${encodeURIComponent(currentPath)}`);
    renderBreadcrumbs(data.breadcrumbs);
    renderFileList(data.items);
    updateActions();
  } catch (e) { toast(e.message, "err"); }
}

function renderBreadcrumbs(crumbs) {
  const bc = $("#breadcrumbs");
  bc.innerHTML = "";
  crumbs.forEach((c, i) => {
    const span = document.createElement("span");
    span.className = "crumb" + (i === crumbs.length - 1 ? " current" : "");
    span.textContent = c.name === "" ? "uploads" : c.name;
    span.onclick = () => { currentPath = c.path; loadFiles(); };
    bc.appendChild(span);
    if (i < crumbs.length - 1) {
      const sep = document.createElement("span");
      sep.className = "crumb-sep"; sep.textContent = "/";
      bc.appendChild(sep);
    }
  });
}

function renderFileList(items) {
  const wrap = $("#fileList");
  wrap.innerHTML = "";
  if (!items.length) {
    wrap.innerHTML = `<div class="empty"><div class="ico">📂</div>Kosong — unggah file di sini</div>`;
    return;
  }
  const header = document.createElement("div");
  header.className = "file-header";
  header.innerHTML = `<div></div><div>Nama</div><div>Ukuran</div><div>Diubah</div><div></div>`;
  wrap.appendChild(header);
  const list = document.createElement("div");
  list.className = "file-list";
  items.forEach(it => {
    const row = document.createElement("div");
    row.className = "file-row";
    row.dataset.path = it.path;
    row.innerHTML = `
      <div class="chk"><input type="checkbox" data-path="${it.path}"></div>
      <div class="name"><span class="ico">${iconFor(it.name, it.is_dir)}</span> ${esc(it.name)}</div>
      <div class="size">${it.is_dir ? "" : it.human_size}</div>
      <div class="date">${it.modified}</div>
      <div class="dl"></div>`;
    row.querySelector(".name").onclick = () => {
      if (it.is_dir) { currentPath = it.path; loadFiles(); }
    };
    row.querySelector("input").onchange = (e) => {
      if (e.target.checked) { selected.add(it.path); row.classList.add("selected"); }
      else { selected.delete(it.path); row.classList.remove("selected"); }
      updateActions();
    };
    list.appendChild(row);
  });
  wrap.appendChild(list);
}

function esc(s) {
  const d = document.createElement("div"); d.textContent = s; return d.innerHTML;
}

// ---------- Actions ----------
function updateActions() {
  const n = selected.size;
  $("#compressBtn").disabled = currentTab !== "files" || n === 0;
  $("#deleteBtn").disabled = currentTab !== "files" || n === 0;
  $("#selCount").innerHTML = n ? `<b>${n}</b> dipilih` : "tidak ada pilihan";
}

// ---------- Upload ----------
function setupUpload() {
  const dz = $("#dropzone");
  const input = $("#fileInput");
  dz.onclick = () => input.click();
  input.onchange = () => uploadFiles(input.files);
  ["dragover", "dragenter"].forEach(ev => dz.addEventListener(ev, e => {
    e.preventDefault(); dz.classList.add("drag");
  }));
  ["dragleave", "drop"].forEach(ev => dz.addEventListener(ev, e => {
    e.preventDefault(); dz.classList.remove("drag");
  }));
  dz.addEventListener("drop", e => {
    if (e.dataTransfer.files.length) uploadFiles(e.dataTransfer.files);
  });
}

async function uploadFiles(files) {
  const prog = $("#progress");
  prog.classList.add("show");
  prog.querySelector(".bar").style.width = "30%";
  const fd = new FormData();
  fd.append("path", currentPath);
  for (const f of files) fd.append("files", f);
  try {
    const data = await api("upload", { method: "POST", body: fd });
    prog.querySelector(".bar").style.width = "100%";
    toast(`${data.count} file berhasil diunggah`);
    loadFiles();
  } catch (e) { toast(e.message, "err"); }
  setTimeout(() => { prog.classList.remove("show"); prog.querySelector(".bar").style.width = "0"; }, 600);
}

// ---------- Compress modal ----------
function openCompressModal() {
  if (!selected.size) return;
  const fmtSel = $("#compFormat");
  fmtSel.innerHTML = "";
  Object.entries(window.FORMATS).forEach(([k, v]) => {
    const o = document.createElement("option"); o.value = k; o.textContent = v;
    fmtSel.appendChild(o);
  });
  const itemsBox = $("#compItems");
  itemsBox.innerHTML = selected.size
    ? Array.from(selected).map(p => `<div class="it">📦 ${esc(p.split("/").pop())}</div>`).join("")
    : `<div class="it">(tidak ada)</div>`;
  $("#modalCompress").classList.add("show");
}

async function doCompress() {
  const fmt = $("#compFormat").value;
  $("#compBtn").disabled = true;
  try {
    const data = await api("compress", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ items: Array.from(selected), format: fmt }),
    });
    toast(`Arsip dibuat: ${data.archive} (${data.human_size})`, "ok");
    closeModal("modalCompress");
    selected.clear();
    setTab("archives");
  } catch (e) { toast(e.message, "err"); }
  $("#compBtn").disabled = false;
}

// ---------- Mkdir ----------
async function doMkdir() {
  const name = $("#mkdirName").value.trim();
  if (!name) return;
  try {
    await api("mkdir", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path: currentPath, name }),
    });
    toast("Folder dibuat");
    closeModal("modalMkdir");
    $("#mkdirName").value = "";
    loadFiles();
  } catch (e) { toast(e.message, "err"); }
}

// ---------- Delete ----------
async function doDelete() {
  if (!selected.size) return;
  if (!confirm(`Hapus ${selected.size} item?`)) return;
  for (const p of Array.from(selected)) {
    try {
      await api("delete", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ path: p }),
      });
    } catch (e) { toast(e.message, "err"); }
  }
  toast("Item dihapus");
  selected.clear();
  loadFiles();
}

// ---------- Archives ----------
async function loadArchives() {
  try {
    const data = await api("archives");
    renderArchives(data.items);
  } catch (e) { toast(e.message, "err"); }
}

function renderArchives(items) {
  const wrap = $("#fileList");
  wrap.innerHTML = "";
  $("#breadcrumbs").innerHTML = `<span class="crumb current">archives</span>`;
  if (!items.length) {
    wrap.innerHTML = `<div class="empty"><div class="ico">🗜️</div>Belum ada arsip. Kompres file untuk membuat arsip.</div>`;
    return;
  }
  const header = document.createElement("div");
  header.className = "file-header";
  header.innerHTML = `<div></div><div>Nama Arsip</div><div>Ukuran</div><div>Dibuat</div><div></div>`;
  wrap.appendChild(header);
  const list = document.createElement("div");
  list.className = "file-list";
  items.forEach(it => {
    const row = document.createElement("div");
    row.className = "file-row";
    row.innerHTML = `
      <div class="chk"></div>
      <div class="name"><span class="ico">${iconFor(it.name, false)}</span> ${esc(it.name)}</div>
      <div class="size">${it.human_size}</div>
      <div class="date">${it.modified}</div>
      <div class="dl">
        <button class="btn-blue" style="padding:4px 8px;font-size:11px" data-act="dl">⬇</button>
        <button class="btn-green" style="padding:4px 8px;font-size:11px" data-act="ex">⬆</button>
        <button class="btn-danger" style="padding:4px 8px;font-size:11px" data-act="del">✕</button>
      </div>`;
    row.querySelector('[data-act="dl"]').onclick = () => downloadArchive(it.path);
    row.querySelector('[data-act="ex"]').onclick = () => extractArchive(it.path, it.name);
    row.querySelector('[data-act="del"]').onclick = () => deleteArchive(it.path);
    list.appendChild(row);
  });
  wrap.appendChild(list);
}

function downloadArchive(path) {
  window.location = `/api/archives/download?path=${encodeURIComponent(path)}`;
}

async function deleteArchive(path) {
  if (!confirm("Hapus arsip ini?")) return;
  try {
    await api("archives/delete", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path }),
    });
    toast("Arsip dihapus");
    loadArchives();
  } catch (e) { toast(e.message, "err"); }
}

async function extractArchive(path, name) {
  try {
    const data = await api("extract", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path, subdir: name + "_extracted" }),
    });
    toast(`Diekstrak ke ${data.subdir}`);
    setTab("extracted");
  } catch (e) { toast(e.message, "err"); }
}

async function viewArchiveContents(path, name) {
  try {
    const data = await api(`archives/contents?path=${encodeURIComponent(path)}`);
    $("#archiveContentsName").textContent = name;
    const tree = $("#archiveTree");
    tree.innerHTML = "";
    data.items.forEach(it => {
      const d = document.createElement("div");
      d.className = "te" + (it.is_dir ? " dir" : "");
      const depth = it.name.split("/").length - 1;
      d.style.paddingLeft = (depth * 14) + "px";
      d.textContent = (it.is_dir ? "📁 " : "📄 ") + it.name.split("/").pop() + (it.is_dir ? "" : `  (${it.human_size})`);
      tree.appendChild(d);
    });
    $("#modalContents").classList.add("show");
  } catch (e) { toast(e.message, "err"); }
}

// ---------- Extracted ----------
async function loadExtracted() {
  try {
    const r = await fetch(`/api/extracted/list?path=${encodeURIComponent(currentPath)}`);
    const d = await r.json();
    if (!r.ok) throw new Error(d.error || `HTTP ${r.status}`);
    const crumbs = [{ name: "extracted", path: "" }];
    let accum = "";
    currentPath.split("/").filter(Boolean).forEach(p => {
      accum = accum ? accum + "/" + p : p;
      crumbs.push({ name: p, path: accum });
    });
    renderBreadcrumbs(crumbs);
    renderExtractedList(d.items);
  } catch (e) { toast(e.message, "err"); }
}

function renderExtractedList(items) {
  const wrap = $("#fileList");
  wrap.innerHTML = "";
  if (!items.length) {
    wrap.innerHTML = `<div class="empty"><div class="ico">📦</div>Belum ada file terekstrak</div>`;
    return;
  }
  const header = document.createElement("div");
  header.className = "file-header";
  header.innerHTML = `<div></div><div>Nama</div><div>Ukuran</div><div>Diubah</div><div></div>`;
  wrap.appendChild(header);
  const list = document.createElement("div");
  list.className = "file-list";
  items.forEach(it => {
    const row = document.createElement("div");
    row.className = "file-row";
    row.innerHTML = `
      <div class="chk"></div>
      <div class="name"><span class="ico">${iconFor(it.name, it.is_dir)}</span> ${esc(it.name)}</div>
      <div class="size">${it.is_dir ? "" : it.human_size}</div>
      <div class="date">${it.modified}</div>
      <div class="dl">${it.is_dir ? "" : `<button class="btn-blue" style="padding:4px 8px;font-size:11px">⬇</button>`}</div>`;
    row.querySelector(".name").onclick = () => {
      if (it.is_dir) { currentPath = it.path; loadExtracted(); }
    };
    const dlBtn = row.querySelector("button");
    if (dlBtn) dlBtn.onclick = (e) => { e.stopPropagation(); downloadExtracted(it.path); };
    list.appendChild(row);
  });
  wrap.appendChild(list);
}

function downloadExtracted(path) {
  window.location = `/api/extracted/download?path=${encodeURIComponent(path)}`;
}

// ---------- Modals ----------
function closeModal(id) { $("#" + id).classList.remove("show"); }

function setupModals() {
  $$(".modal-bg").forEach(m => {
    m.addEventListener("click", e => { if (e.target === m) m.classList.remove("show"); });
  });
}

// ---------- Init ----------
window.FORMATS = {};
document.addEventListener("DOMContentLoaded", () => {
  window.FORMATS = JSON.parse($("#formatData").textContent);
  setupUpload();
  setupModals();

  $("#btnCompress").onclick = openCompressModal;
  $("#btnDelete").onclick = doDelete;
  $("#btnMkdir").onclick = () => $("#modalMkdir").classList.add("show");
  $("#btnExtract").onclick = () => setTab("archives");
  $("#btnRefresh").onclick = () => setTab(currentTab);

  $("#compBtn").onclick = doCompress;
  $("#compCancel").onclick = () => closeModal("modalCompress");
  $("#mkdirBtn").onclick = doMkdir;
  $("#mkdirCancel").onclick = () => closeModal("modalMkdir");

  $$(".tab").forEach(t => t.onclick = () => setTab(t.dataset.tab));
  $$(".side-btn").forEach(b => b.onclick = () => setTab(b.dataset.tab));

  setTab("files");
});
