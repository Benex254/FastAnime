import os
import sys

if __package__ is None and not getattr(sys, "frozen", False):
    # direct call of __main__.py
    import os.path

    path = os.path.realpath(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(os.path.dirname(path)))


if __name__ == "__main__":
    in_development = bool(os.environ.get("FA_DEVELOPMENT", False))
    from . import FastAnime

    if in_development:
        FastAnime()
    else:
        try:
            FastAnime()
        except Exception as e:
            from .Utility.utils import write_crash

            write_crash(e)
