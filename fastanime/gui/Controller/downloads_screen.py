from ..Model.download_screen import DownloadsScreenModel
from ..View.DownloadsScreen.download_screen import DownloadsScreenView


class DownloadsScreenController:
    """The controller for the download screen"""

    def __init__(self, model: DownloadsScreenModel):
        self.model = model
        self.view = DownloadsScreenView(controller=self, model=self.model)

    def get_view(self) -> DownloadsScreenView:
        return self.view


__all__ = ["DownloadsScreenController"]
