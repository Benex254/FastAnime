import pathlib
import re
import shlex
import shutil
import sys
from subprocess import PIPE, Popen

import requests
from rich import print

from .. import APP_NAME, AUTHOR, GIT_REPO, REPO, __version__

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
        return (release_json["tag_name"] == __version__, release_json)
    else:
        print(request.text)
        return (False, {})


def is_git_repo(author, repository):
    # Check if the current directory contains a .git folder
    if not pathlib.Path("./.git").exists():
        return False

    repository_qualname = f"{author}/{repository}"

    # Read the .git/config file to find the remote repository URL
    config_path = pathlib.Path("./.git/config")
    if not config_path.exists():
        return False
    print("here")

    with open(config_path, "r") as git_config:
        git_config_content = git_config.read()

    # Use regex to find the repository URL in the config file
    repo_name_pattern = r"\[remote \"origin\"\]\s+url = .*\/([^/]+\/[^/]+)\.git"
    match = re.search(repo_name_pattern, git_config_content)
    print(match)

    if match is None:
        return False

    # Extract the repository name and compare with the expected repository_qualname
    config_repo_name = match.group(1)
    return config_repo_name == repository_qualname


def update_app():
    is_latest, release_json = check_for_updates()
    if is_latest:
        print("[green]App is up to date[/]")
        return
    tag_name = release_json["tag_name"]

    print("[cyan]Updating app to version %s[/]" % tag_name)
    if is_git_repo(AUTHOR, APP_NAME):
        executable = shutil.which("git")
        args = [
            executable,
            "pull",
        ]

        print(f"Pulling latest changes from the repository via git: {shlex.join(args)}")

        if not executable:
            return print("[red]Cannot find git.[/]")

        process = Popen(
            args,
            stdout=PIPE,
            stderr=PIPE,
        )

        process.communicate()
    else:
        executable = sys.executable

        app_package_url = f"https://{REPO}/releases/download/{tag_name}/fastanime-{tag_name.replace("v","")}.tar.gz"
        args = [
            executable,
            "-m",
            "pip",
            "install",
            app_package_url,
            "--user",
            "--no-warn-script-location",
        ]
        process = Popen(args)
        process.communicate()
