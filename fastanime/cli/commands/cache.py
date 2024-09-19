import click


@click.command(
    help="Helper command to manage cache",
    epilog="""
\b
\b\bExamples:
  # delete everything in the cache dir
  fastanime cache --clean
\b
  # print the path to the cache dir and exit
  fastanime cache --path
\b
  # print the current size of the cache dir and exit
  fastanime cache --size
\b
  # open the cache dir and exit
  fastanime cache
""",
)
@click.option("--clean", help="Clean the cache dir", is_flag=True)
@click.option("--path", help="The path to the cache dir", is_flag=True)
@click.option("--size", help="The size of the cache dir", is_flag=True)
def cache(clean, path, size):
    from ...constants import APP_CACHE_DIR

    if path:
        print(APP_CACHE_DIR)
    elif clean:
        import shutil

        from rich.prompt import Confirm

        if Confirm.ask(
            f"Are you sure you want to clean the following path: {APP_CACHE_DIR};(NOTE: !!The action is irreversible and will clean your cache!!)",
            default=False,
        ):
            print("Cleaning...")
            shutil.rmtree(APP_CACHE_DIR)
            print("Successfully removed: ", APP_CACHE_DIR)
    elif size:
        import os

        from ..utils.utils import format_bytes_to_human

        total_size = 0
        for dirpath, dirnames, filenames in os.walk(APP_CACHE_DIR):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        print("Total Size: ", format_bytes_to_human(total_size))
    else:
        import click

        click.launch(APP_CACHE_DIR)
