import os
import playwright_stealth

block_cipher = None

stealth_js_path = os.path.join(os.path.dirname(playwright_stealth.__file__), 'js')

import playwright
playwright_driver_path = os.path.join(os.path.dirname(playwright.__file__), 'driver')

added_files = [
    ('app/assets', 'app/assets'),
    ('.env', '.'),
    (stealth_js_path, 'playwright_stealth/js'),
    (playwright_driver_path, 'playwright/driver'),
]

a = Analysis(
    ['app/main.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=['google.generativeai', 'fitz', 'playwright', 'playwright_stealth', 'docx', 'httpx', 'bs4', 'ebooklib'],
    hookspath=[],
    hooksconfig={},
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
    name='CariKitab',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['app/assets/logo.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='CariKitab',
)
