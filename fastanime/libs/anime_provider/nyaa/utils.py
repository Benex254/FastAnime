import logging
import os
import sys
import time

import libtorrent  # pyright: ignore
from rich import print
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)

logger = logging.getLogger("nyaa")


def download_torrent(
    filename: str,
    result_filename: str | None = None,
    show_progress: bool = True,
    base_path: str = "Anime",
) -> str:
    session = libtorrent.session({"listen_interfaces": "0.0.0.0:6881"})
    logger.debug("Started libtorrent session")

    base_path = os.path.expanduser(base_path)
    logger.debug(f"Downloading output to: '{base_path}'")

    info = libtorrent.torrent_info(filename)

    logger.debug("Started downloading torrent")
    handle: libtorrent.torrent_handle = session.add_torrent(
        {"ti": info, "save_path": base_path}
    )

    status: libtorrent.session_status = handle.status()

    progress_bar = Progress(
        "[progress.description]{task.description}",
        BarColumn(bar_width=None),
        "[progress.percentage]{task.percentage:>3.1f}%",
        "•",
        DownloadColumn(),
        "•",
        TransferSpeedColumn(),
        "•",
        TimeRemainingColumn(),
        "•",
        TextColumn("[green]Peers: {task.fields[peers]}[/green]"),
    )

    if show_progress:
        with progress_bar:
            download_task = progress_bar.add_task(
                "downloading",
                filename=status.name,
                total=status.total_wanted,
                peers=0,
                start=False,
            )

            while not status.total_done:
                # Checking files
                status = handle.status()
                description = "[bold yellow]Checking files[/bold yellow]"
                progress_bar.update(
                    download_task,
                    completed=status.total_done,
                    peers=status.num_peers,
                    description=description,
                )

            # Started download
            progress_bar.start_task(download_task)
            description = f"[bold blue]Downloading[/bold blue] [bold yellow]{result_filename}[/bold yellow]"

            while not status.is_seeding:
                status = handle.status()

                progress_bar.update(
                    download_task,
                    completed=status.total_done,
                    peers=status.num_peers,
                    description=description,
                )

                alerts = session.pop_alerts()

                alert: libtorrent.alert
                for alert in alerts:
                    if (
                        alert.category()
                        & libtorrent.alert.category_t.error_notification
                    ):
                        logger.debug(f"[Alert] {alert}")

                time.sleep(1)

            progress_bar.update(
                download_task,
                description=f"[bold blue]Finished Downloading[/bold blue] [bold green]{result_filename}[/bold green]",
                completed=status.total_wanted,
            )

    if result_filename:
        old_name = f"{base_path}/{status.name}"
        new_name = f"{base_path}/{result_filename}"

        os.rename(old_name, new_name)

        logger.debug(f"Finished torrent download, renamed '{old_name}' to '{new_name}'")

        return new_name

    return ""


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("You need to pass in the .torrent file path.")
        sys.exit(1)

    download_torrent(sys.argv[1])
