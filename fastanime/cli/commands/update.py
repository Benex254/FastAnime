import click


@click.command(
    help="Helper command to update fastanime to latest",
    epilog="""
\b
\b\bExamples:
  # update fastanime to latest
  fastanime update
\b
  # check for latest release
  fastanime update --check
""",
)
@click.option("--check", "-c", help="Check for the latest release", is_flag=True)
def update(
    check,
):
    from rich.console import Console
    from rich.markdown import Markdown

    from ... import __version__
    from ..app_updater import check_for_updates, update_app

    def _print_release(release_data):
        console = Console()
        body = Markdown(release_data["body"])
        tag = github_release_data["tag_name"]
        tag_title = release_data["name"]
        github_page_url = release_data["html_url"]
        console.print(f"Release Page: {github_page_url}")
        console.print(f"Tag: {tag}")
        console.print(f"Title: {tag_title}")
        console.print(body)

    if check:
        is_latest, github_release_data = check_for_updates()
        if not is_latest:
            print(
                f"You are running an older version ({__version__}) of fastanime please update to get the latest features"
            )
            _print_release(github_release_data)
        else:
            print(f"You are running the latest version ({__version__}) of fastanime")
            _print_release(github_release_data)
    else:
        success, github_release_data = update_app()
        _print_release(github_release_data)
        if success:
            print("Successfully updated")
        else:
            print("failed to update")
