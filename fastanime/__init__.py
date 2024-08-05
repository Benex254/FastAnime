import os
import plyer
from kivy.resources import resource_add_path

app_dir = os.path.abspath(os.path.dirname(__file__))


data_folder = os.path.join(app_dir, "data")
if not os.path.exists(data_folder):
    os.mkdir(data_folder)


if vid_path := plyer.storagepath.get_videos_dir():  # type: ignore
    downloads_dir = os.path.join(vid_path, "FastAnime")
    if not os.path.exists(downloads_dir):
        os.mkdir(downloads_dir)
else:
    downloads_dir = os.path.join(".", "videos")
    if not os.path.exists(downloads_dir):
        os.mkdir(downloads_dir)


assets_folder = os.path.join(app_dir, "assets")
resource_add_path(assets_folder)
conigs_folder = os.path.join(app_dir, "configs")
resource_add_path(conigs_folder)
