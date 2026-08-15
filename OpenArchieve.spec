# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for OpenArchieve
# Build: pyinstaller OpenArchieve.spec
# Windows .exe: run this spec on Windows; output in dist/OpenArchieve[.exe]

import os

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('templates', 'templates'),
        ('static', 'static'),
    ],
    hiddenimports=[
        'flask',
        'jinja2',
        'werkzeug',
        'markupsafe',
        'itsdangerous',
        'click',
        'zipfile',
        'tarfile',
        'gzip',
        'bz2',
        'lzma',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'pytest', 'unittest'],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='OpenArchieve',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    runtime_tmpdir=None,
    console=True,
    icon=None,  # set to 'icon.ico' on Windows if you have one
)
