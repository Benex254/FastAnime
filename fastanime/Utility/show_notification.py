from kivy.clock import Clock
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarSupportingText, MDSnackbarText


def show_notification(title, details):
    """helper function to display notifications

    Args:
        title (str): the title of your message
        details (str): the details of your message
    """

    def _show(dt):
        MDSnackbar(
            MDSnackbarText(
                text=title,
                adaptive_height=True,
            ),
            MDSnackbarSupportingText(
                text=details, shorten=False, max_lines=0, adaptive_height=True
            ),
            duration=5,
            y="10dp",
            pos_hint={"bottom": 1, "right": 0.99},
            padding=[0, 0, "8dp", "8dp"],
            size_hint_x=0.4,
        ).open()

    Clock.schedule_once(_show, 1)
