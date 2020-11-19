# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['.\\SRC\\main.py',
            '.\\SRC\\appDir.py',
            '.\\SRC\\communication.py',
            '.\\SRC\\debugWidgets\\RecieverWidget.py',
            '.\\SRC\\debugWidgets\\SendWidget.py'],
             pathex=[ 'D:\\SourceCode\\Python\\DSPdebugTool'],
             binaries=[],
             datas=[],
             hiddenimports=['appDir','RecieverWidget','SendWidget','TransmitMessageThread','ReceiveMessageThread'],
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
          [],
          exclude_binaries=True,
          name='DSPdebugTool',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False , icon='debugTool.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='DSPdebugTool')
