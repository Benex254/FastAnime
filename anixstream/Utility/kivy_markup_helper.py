"""
Contains helper functions to make your life easy when adding kivy markup to text
"""

from kivy.utils import get_hex_from_color


def bolden(text: str):
    return f"[b]{text}[/b]"


def italicize(text: str):
    return f"[i]{text}[/i]"


def underline(text: str):
    return f"[u]{text}[/u]"


def strike_through(text: str):
    return f"[s]{text}[/s]"


def sub_script(text: str):
    return f"[sub]{text}[/sub]"


def super_script(text: str):
    return f"[sup]{text}[/sup]"


def color_text(text: str, color: tuple):
    hex_color = get_hex_from_color(color)
    return f"[color={hex_color}]{text}[/color]"


def font(text: str, font_name: str):
    return f"[font={font_name}]{text}[/font]"


def font_family(text: str, family: str):
    return f"[font_family={family}]{text}[/font_family]"


def font_context(text: str, context: str):
    return f"[font_context={context}]{text}[/font_context]"


def font_size(text: str, size: int):
    return f"[size={size}]{text}[/size]"


def text_ref(text: str, ref: str):
    return f"[ref={ref}]{text}[/ref]"
