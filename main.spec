# -*- mode: python ; coding: utf-8 -*-

import platform

hidden = []
windowed = False
exe_icon = "assets/icons/ymael.png"
if platform.system() == "Windows":
    hidden = ["win32timezone"]
    windowed = True
    exe_icon = "assets/icons/ymael.ico"

block_cipher = None

a = Analysis(['main.py'],
             binaries=[],
             datas=[
                ('assets/icons/ymael.png', '.'),
                ('assets/icons/ymael.ico', '.'),
                ('LICENSE', '.')
             ],
             hiddenimports=hidden,
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='ymael',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          icon=exe_icon,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=not(windowed)
          )
