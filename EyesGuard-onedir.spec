a = Analysis(
    ['src/main.py'],
    pathex=['src'],
    binaries=[],
    datas=[('res', 'res')],
    hiddenimports=['pystray._win32', 'support.sound.windows.sound_player'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'setuptools',
        'pkg_resources',
        'pip',
        'wheel',
        'unittest',
        'pydoc_data',
        'sqlite3',
        'xml',
        'pydantic.v1',
    ],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='EyesGuard',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='res/img/eyes_with_protection.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='EyesGuard',
)
