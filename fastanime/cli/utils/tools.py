from rich.text import Text


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


def get_formatted_str(text: str, style):
    # Create a Text object with desired style
    text = Text("Hello, World!", style="bold red")

    # Convert the Text object to an ANSI string
    ansi_output = text.__rich_console__(None, None)

    # Join the ANSI strings to form the final output
    "".join(segment.text for segment in ansi_output)
