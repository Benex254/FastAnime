import click

from ..interfaces import anime_provider_


@click.command()
@click.pass_obj
def search(
    config,
    anime_title,
):
    anime_provider_(
        config,
        anime_title,
    )
