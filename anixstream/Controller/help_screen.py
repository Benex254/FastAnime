
from anixstream.View import HelpScreenView
from anixstream.Model import HelpScreenModel


class HelpScreenController:
    """The help screen controller
    """
    def __init__(self, model:HelpScreenModel):
        self.model = model
        self.view = HelpScreenView(controller=self, model=self.model)

    def get_view(self) -> HelpScreenView:
        return self.view
