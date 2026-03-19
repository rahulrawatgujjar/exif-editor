# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path


project_root = Path(globals().get('SPECPATH', '.')).resolve()
datas = []
exiftool_binary = project_root / "tools" / "exiftool.exe"
if exiftool_binary.exists():
    datas.append((str(exiftool_binary), "tools"))

exiftool_runtime_dir = project_root / "tools" / "exiftool_files"
if exiftool_runtime_dir.exists() and exiftool_runtime_dir.is_dir():
    for src in exiftool_runtime_dir.rglob("*"):
        if src.is_file():
            relative_parent = src.relative_to(project_root / "tools").parent
            datas.append((str(src), str(Path("tools") / relative_parent)))


a = Analysis(
    ['easy_run.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=['metadata', 'metadata.manager'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ExifEditor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
