# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all

binaries = []
hiddenimports = []
datas = [
   ('bin/writer.cmd', 'bin'),
   ('Themes/Dark/style_rc.py', 'Themes/Dark'),
   ('Themes/Dark/__init__.py', 'Themes/Dark'),
   ('Themes/Light/style_rc.py', 'Themes/Light'),
   ('Themes/Light/__init__.py', 'Themes/Light'),
   ('Templates/writer/metadata.json', 'Templates/writer'), 
   ('Templates/writer/res/layout.html', 'Templates/writer/res'),
]
tmp_ret = collect_all('reportlab.graphics.barcode')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
block_cipher = None
to_exclude = {'opengl32sw.dll', 'Qt5DBus.dll', 'Qt5WebSockets.dll', 'Qt5Svg.dll'}

a = Analysis(['app.py'],
             pathex=[],
             binaries=binaries,
             datas=datas,
             hiddenimports=hiddenimports,
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
             
a.binaries -= [(os.path.normcase(x), None, None) for x in to_exclude]
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts, 
          [],
          exclude_binaries=True,
          name='Writer',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None , version='VersionInfo', icon='./icons/icon.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas, 
               strip=False,
               upx=True,
               upx_exclude=[],
               name='Writer')
