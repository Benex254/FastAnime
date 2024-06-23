from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.utils import format_bytes_to_human

from ...View.base_screen import BaseScreenView
from .components.task_card import TaskCard


class DownloadsScreenView(BaseScreenView):
    main_container = ObjectProperty()
    progress_bar = ObjectProperty()
    download_progress_label = ObjectProperty()

    def new_download_task(self, filename):
        Clock.schedule_once(
            lambda _: self.main_container.add_widget(TaskCard(filename))
        )

    def on_episode_download_progress(self, data):
        percentage_completion = round(
            (data.get("downloaded_bytes", 0) / data.get("total_bytes", 0)) * 100
        )
        speed = format_bytes_to_human(data.get("speed", 0)) if data.get("speed") else 0
        progress_text = f"Downloading: {data.get('filename', 'unknown')} ({format_bytes_to_human(data.get('downloaded_bytes',0)) if data.get('downloaded_bytes') else 0}/{format_bytes_to_human(data.get('total_bytes',0)) if data.get('total_bytes') else 0})\n Elapsed: {round(data.get('elapsed',0)) if data.get('elapsed') else 0}s ETA: {data.get('eta',0) if data.get('eta') else 0}s Speed: {speed}/s"

        self.progress_bar.value = max(min(percentage_completion, 100), 0)
        self.download_progress_label.text = progress_text

    def update_layout(self, widget):
        self.user_anime_list_container.add_widget(widget)

        #
        #     d["filename"],
        #     d["downloaded_bytes"],
        #     d["total_bytes"],
        #     d.get("total_bytes"),
        #     d["elapsed"],
        #     d["eta"],
        #     d["speed"],
        #     d.get("percent"),
        # )
        #


__all__ = ["DownloadsScreenView"]
