# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller配置文件
用于打包Windows可执行文件
"""

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('ui', 'ui'),
        ('modules', 'modules'),
        ('utils', 'utils'),
    ],
    hiddenimports=[
        'PyQt5',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'ping3',
        'psutil',
        'dnspython',
        'speedtest',
        'pysnmp',
        'whois',
        'requests',
        'xml.etree.ElementTree',
        'xml.parsers.expat',
        'http.client',
        'urllib.request',
        'json',
        'socket',
        'threading',
        'queue',
    ],
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
    name='网络故障排查工具',
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
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='网络故障排查工具',
)
