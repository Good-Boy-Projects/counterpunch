# counterpunch.spec
#
# Build with:  pyinstaller packaging/counterpunch.spec   (from repo root)
#         or:  ./packaging/build-app.sh              (from repo root)
# Output:      dist/Counterpunch.app

import os

block_cipher = None

# PyInstaller resolves relative paths in a .spec file relative to the
# spec file's own directory, not the directory you invoke `pyinstaller`
# from. SPECPATH is injected automatically by PyInstaller (absolute path
# to this file's directory) — use it to compute the real repo root and
# build every path from there, explicitly, rather than any bare relative
# string (which silently resolves against packaging/ and double-nests).
REPO_ROOT = os.path.abspath(os.path.join(SPECPATH, ".."))
ICON_PATH = os.path.join(REPO_ROOT, "packaging", "TruFont.icns")

a = Analysis(
    [os.path.join(REPO_ROOT, "Lib", "counterpunch", "__main__.py")],
    pathex=[os.path.join(REPO_ROOT, "Lib")],
    binaries=[],
    datas=[
        (os.path.join(REPO_ROOT, "Lib", "counterpunch", "resources"), "counterpunch/resources"),
    ],
    hiddenimports=[
        "PySide6.QtCore",
        "PySide6.QtGui",
        "PySide6.QtWidgets",
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Counterpunch",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="Counterpunch",
)

app = BUNDLE(
    coll,
    name="Counterpunch.app",
    icon=ICON_PATH if os.path.exists(ICON_PATH) else None,
    bundle_identifier="io.github.yourusername.counterpunch",  # reverse-DNS, adjust
    info_plist={
        "CFBundleName": "Counterpunch",
        "CFBundleDisplayName": "Counterpunch",
        "CFBundleIdentifier": "io.github.yourusername.counterpunch",
        "CFBundleVersion": os.environ.get("TRUFONT_BUILD_VERSION", "0.1.0"),
        "CFBundleShortVersionString": os.environ.get("TRUFONT_BUILD_VERSION", "0.1.0"),
        "NSHighResolutionCapable": True,
        "NSHumanReadableCopyright": "Copyright © 2026 Good Boy Projects. Based on TruFont, Copyright © The TruFont Project Developers.",
    },
)
