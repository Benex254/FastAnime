# -*- mode: python ; coding: utf-8 -*-

import sys
import os

from kivy_deps import sdl2, glew
from kivymd.icon_definitions import md_icons
from kivymd import hooks_path as kivymd_hooks_path

path = os.path.abspath(".")

a = Analysis(
    ["main.py"],
    datas=[ 
('./assets/*', './assets'),("./data/*","./data/*"),("./configs/*","./configs")
 ],
    pathex=[path],
    hiddenimports=["kivymd.icon_definitions.md_icons"],
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
	icon="./assets/logo.ico"
)