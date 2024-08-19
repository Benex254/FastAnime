# TODO: add typing
class FastAnimeRuntimeState(dict):
    """A class that manages fastanime runtime during anilist command runtime"""

    def __getattr__(self, attr):
        try:
            return self.__getitem__(attr)
        except KeyError:
            raise AttributeError(
                "%r object has no attribute %r" % (self.__class__.__name__, attr)
            )

    def __setattr__(self, attr, value):
        self.__setitem__(attr, value)


def exit_app(exit_code=0, *args):
    import sys

    from rich.console import Console

    from ...constants import APP_NAME, ICON_PATH, USER_NAME

    console = Console()
    if not console.is_terminal:
        from plyer import notification

        notification.notify(
            app_name=APP_NAME,
            app_icon=ICON_PATH,
            message=f"Have a good day {USER_NAME}",
            title="Shutting down",
        )  # pyright:ignore
    else:
        console.clear()
        console.print("Have a good day :smile:", USER_NAME)
    sys.exit(exit_code)
