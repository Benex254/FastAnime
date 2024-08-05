from ..View import CrashLogScreenView
from ..Model import CrashLogScreenModel


class CrashLogScreenController:
    """The crash log screen controller"""

    def __init__(self, model: CrashLogScreenModel):
        self.model = model
        self.view = CrashLogScreenView(controller=self, model=self.model)
        # self.update_anime_view()

    def get_view(self) -> CrashLogScreenView:
        return self.view
