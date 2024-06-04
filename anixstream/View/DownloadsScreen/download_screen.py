from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.utils import format_bytes_to_human

from ...View.base_screen import BaseScreenView
from .components.task_card import TaskCard


class DownloadsScreenView(BaseScreenView):
    main_container = ObjectProperty()
    progress_bar = ObjectProperty()
    download_progress_label = ObjectProperty()

    def on_new_download_task(self, anime_title: str, episodes: str | None):
        if not episodes:
            episodes = "All"
        Clock.schedule_once(
            lambda _: self.main_container.add_widget(TaskCard(anime_title, episodes))
        )

    def on_episode_download_progress(
        self, current_bytes_downloaded, total_bytes, episode_info
    ):
        percentage_completion = round((current_bytes_downloaded / total_bytes) * 100)
        progress_text = f"Downloading: {episode_info['anime_title']} - {episode_info['episode']} ({format_bytes_to_human(current_bytes_downloaded)}/{format_bytes_to_human(total_bytes)})"
        if (percentage_completion % 5) == 0:
            self.progress_bar.value = max(min(percentage_completion, 100), 0)
            self.download_progress_label.text = progress_text

    def update_layout(self, widget):
        self.user_anime_list_container.add_widget(widget)
