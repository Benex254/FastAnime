# -*- mode: python ; coding: utf-8 -*-

import sys
import os

from kivy_deps import sdl2, glew
from kivymd.icon_definitions import md_icons
from kivymd import hooks_path as kivymd_hooks_path

path = os.path.abspath(".")

kv_file_paths = []

app_dir = os.path.join(os.getcwd(),"anixstream")
print(app_dir)

views_folder = os.path.join(app_dir,"View")
for dirpath,dirnames,filenames in os.walk(views_folder):
    for filename in filenames:
        if os.path.splitext(filename)[1]==".kv":
            kv_file = os.path.join(dirpath,filename)
            kv_file_paths.append((kv_file,"./Views/"))



a = Analysis(
    ['./anixstream/__main__.py'],
    datas=[ *kv_file_paths,
(f'{app_dir}./assets/*', './assets/'),(f"{app_dir}./data/*","./data/"),(f"{app_dir}./configs/*","./configs/")
 ],
    pathex=[path],
    hiddenimports=["kivymd.icon_definitions.md_icons","plyer.platforms","plyer.platforms.win","plyer.platforms.win.storagepath","win32timezone"],
    hookspath=[kivymd_hooks_path],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
    debug=False,
    strip=False,
    upx=True,
    name="AniXStream",
    console=False,
	icon=f"{app_dir}./assets/logo.ico",
    exclude_binaries=True,
    bootloader_ignore_signals=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
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
    name='AniXStream',
)
