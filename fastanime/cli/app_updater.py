import pathlib
import re
import shlex
import shutil
import subprocess
import sys

import requests
from rich import print

from .. import APP_NAME, AUTHOR, GIT_REPO, __version__

API_URL = f"https://api.{GIT_REPO}/repos/{AUTHOR}/{APP_NAME}/releases/latest"


def check_for_updates():
    USER_AGENT = f"{APP_NAME} user"
    request = requests.get(
        API_URL,
        headers={
            "User-Agent": USER_AGENT,
            "X-GitHub-Api-Version": "2022-11-28",
            "Accept": "application/vnd.github+json",
        },
    )

    if request.status_code == 200:
        release_json = request.json()
        remote_tag = list(
            map(int, release_json["tag_name"].replace("v", "").split("."))
        )
        local_tag = list(map(int, __version__.replace("v", "").split(".")))
        if (
            (remote_tag[0] > local_tag[0])
            or (remote_tag[1] > local_tag[1] and remote_tag[0] == local_tag[0])
            or (
                remote_tag[2] > local_tag[2]
                and remote_tag[0] == local_tag[0]
                and remote_tag[1] == local_tag[1]
            )
        ):
            is_latest = False
        else:
            is_latest = True

        return (is_latest, release_json)
    else:
        print(request.text)
        return (False, {})


def is_git_repo(author, repository):
    # Check if the current directory contains a .git folder
    git_dir = pathlib.Path(".git")
    if not git_dir.exists() or not git_dir.is_dir():
        return False

    # Check if the config file exists
    config_path = git_dir / "config"
    if not config_path.exists():
        return False

    try:
        # Read the .git/config file to find the remote repository URL
        with config_path.open("r") as git_config:
            git_config_content = git_config.read()
    except (FileNotFoundError, PermissionError):
        return False

    # Use regex to find the repository URL in the config file
    repo_name_pattern = r"url\s*=\s*.+/([^/]+/[^/]+)\.git"
    match = re.search(repo_name_pattern, git_config_content)

    # Return True if match found and repository name matches
    return bool(match) and match.group(1) == f"{author}/{repository}"


def update_app():
    is_latest, release_json = check_for_updates()
    if is_latest:
        print("[green]App is up to date[/]")
        return False, release_json
    tag_name = release_json["tag_name"]

    print("[cyan]Updating app to version %s[/]" % tag_name)
    if is_git_repo(AUTHOR, APP_NAME):
        GIT_EXECUTABLE = shutil.which("git")
        args = [
            GIT_EXECUTABLE,
            "pull",
        ]

        print(f"Pulling latest changes from the repository via git: {shlex.join(args)}")

        if not GIT_EXECUTABLE:
            print("[red]Cannot find git please install it.[/]")
            return False, release_json

        process = subprocess.run(
            args,
        )

    else:
        if PIPX_EXECUTABLE := shutil.which("pipx"):
            process = subprocess.run([PIPX_EXECUTABLE, "upgrade", APP_NAME])
        else:
            PYTHON_EXECUTABLE = sys.executable

            args = [
                PYTHON_EXECUTABLE,
                "-m",
                "pip",
                "install",
                APP_NAME,
                "-U",
                "--user",
                "--no-warn-script-location",
            ]
            process = subprocess.run(args)
    if process.returncode == 0:
        return True, release_json
    else:
        return False, release_json
