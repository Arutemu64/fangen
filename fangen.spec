# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller build spec for FANGEN.

Produces an *onedir* Windows build (``dist/fangen/`` containing ``fangen.exe``
and an ``_internal`` folder). Onedir is preferred over onefile: it starts
faster and, because nothing is self-extracted to a temp directory at runtime,
it trips far fewer antivirus heuristics.

Build with:

    pyinstaller fangen.spec --clean --noconfirm
"""

from pathlib import Path

from PyInstaller.utils.hooks import collect_all

# yt-dlp lazily imports its extractors / post-processors and adaptix generates
# its loaders dynamically. PyInstaller's static import analysis misses both, so
# a naive build succeeds but crashes at runtime the moment `download_files` or
# config loading runs. `collect_all` pulls in each package's submodules, data
# files and binaries so the frozen app behaves like the source app.
datas: list = []
binaries: list = []
hiddenimports: list = []
for _pkg in ("yt_dlp", "adaptix"):
    _datas, _binaries, _hiddenimports = collect_all(_pkg)
    datas += _datas
    binaries += _binaries
    hiddenimports += _hiddenimports

# Optional Windows icon: drop an `icon.ico` next to this spec to embed it.
_icon = "icon.ico" if Path("icon.ico").exists() else None


a = Analysis(
    ["src/fangen/__main__.py"],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
    [],
    exclude_binaries=True,
    name="fangen",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    # UPX is intentionally disabled: compressing the binary is a well-known
    # trigger for antivirus false positives and offers little benefit here.
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=_icon,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="fangen",
)
