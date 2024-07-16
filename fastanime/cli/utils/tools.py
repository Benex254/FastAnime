class QueryDict(dict):
    """dot.notation access to dictionary attributes"""

    def __getattr__(self, attr):
        try:
            return self.__getitem__(attr)
        except KeyError:
            raise AttributeError(
                "%r object has no attribute %r" % (self.__class__.__name__, attr)
            )

    def __setattr__(self, attr, value):
        self.__setitem__(attr, value)


def exit_app(*args):
    import sys

    from rich import print

    from ... import USER_NAME

    print("Have a good day :smile:", USER_NAME)
    sys.exit(0)


def get_formatted_str(string: str, style):
    from rich.text import Text

    # Create a Text object with desired style
    text = Text(string, style="bold red")

    # Convert the Text object to an ANSI string
    ansi_output = text.__rich_console__(None, None)  # pyright:ignore

    # Join the ANSI strings to form the final output
    "".join(segment.text for segment in ansi_output)
