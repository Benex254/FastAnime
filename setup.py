import os
import sys

from setuptools import find_packages, setup

assert sys.version_info >= (3, 10, 0), "FastAnime requires python 3.10+"


path = os.path.abspath(".")

kv_file_paths = []

app_dir = os.path.join(path, "fastanime")
print(app_dir)

views_folder = os.path.join(app_dir, "View")
for dirpath, dirnames, filenames in os.walk(views_folder):
    for filename in filenames:
        if os.path.splitext(filename)[1] == ".kv":
            kv_file = os.path.join(dirpath, filename)
            kv_file_paths.append(kv_file)


if __name__ == "__main__":
    setup(
        version="0.2.0",
        packages=[
            *find_packages(
                include=[
                    "fastanime",
                    "fastanime.*",
                    "fastanime.Utility.*",
                    "fastanime.libs.*",
                ]
            ),
        ],
        package_dir={"fastanime": "fastanime"},
        package_data={
            "fastanime": [
                "assets/*",
                "configs/*",
                *kv_file_paths,
            ]
        },
        install_requires=[
            "kivy",
            "plyer",
            "fuzzywuzzy",
            "python-Levenshtein",
            "kivymd @ https://github.com/kivymd/KivyMD/archive/master.zip",
            "ffpyplayer",
            "yt-dlp",
            "pyshortcuts",
        ],
        setup_requires=[],
        python_requires=">=3.10",
        entry_points={
            "gui_scripts": [
                "fastanime = fastanime.__main__:run_app",
            ],
        },
    )
