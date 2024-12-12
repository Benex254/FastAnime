<p align="center">
  <h1 align="center">FastAnime</h1>
</p>
<p align="center">
  <sup>
  Browse anime from the terminal
  </sup>
</p>
<div align="center">
  
![PyPI - Downloads](https://img.shields.io/pypi/dm/fastanime) ![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/FastAnime/FastAnime/test.yml?label=Tests)
![Discord](https://img.shields.io/discord/1250887070906323096?label=Discord)
![GitHub Issues or Pull Requests](https://img.shields.io/github/issues/FastAnime/FastAnime)
![GitHub deployments](https://img.shields.io/github/deployments/FastAnime/fastanime/pypi?label=PyPi%20Publish)
![PyPI - License](https://img.shields.io/pypi/l/fastanime)
![Static Badge](https://img.shields.io/badge/lines%20of%20code-13k%2B-green)
</div>

<p align="center">
<a href="https://discord.gg/HBEmAwvbHV">
<img src="https://invidget.switchblade.xyz/C4rhMA4mmK">
</a>
</p>

![fastanime](https://github.com/user-attachments/assets/9ab09f26-e4a8-4b70-a315-7def998cec63)

<details>
  <summary>
    <b>How it looks</b>
  </summary>

**Anilist results menu:**
![image](https://github.com/user-attachments/assets/240023a7-7e4e-47dd-80ff-017d65081ee1)

**Episodes menu preview:**
![image](https://github.com/user-attachments/assets/580f86ef-326f-4ab3-9bd8-c1cb312fbfa6)

**Without preview images enabled:**
![image](https://github.com/user-attachments/assets/e1248a85-438f-4758-ae34-b0e0b224addd)

**Desktop notifications + episodes menu without image preview:**
![image](https://github.com/user-attachments/assets/b7802ef1-ca0d-45f5-a13a-e39c96a5d499)

</details>


## Installation

![Windows](https://img.shields.io/badge/-Windows_x64-blue.svg?style=for-the-badge&logo=windows)
![Linux/BSD](https://img.shields.io/badge/-Linux/BSD-red.svg?style=for-the-badge&logo=linux)
![Arch Linux](https://img.shields.io/badge/-Arch_Linux-black.svg?style=for-the-badge&logo=archlinux)
![MacOS](https://img.shields.io/badge/-MacOS-lightblue.svg?style=for-the-badge&logo=apple)
![Android](https://img.shields.io/badge/-Android-green.svg?style=for-the-badge&logo=android)

The app can run wherever python can run. So all you need to have is python installed on your device.
On android you can use [termux](https://github.com/termux/termux-app).
If you have any difficulty consult for help on the [discord channel](https://discord.gg/HBEmAwvbHV)

### Installation on nixos

![Static Badge](https://img.shields.io/badge/NixOs-black?style=flat&logo=nixos)

```bash
nix profile install github:Benexl/fastanime
```

### Installation using your favourite package manager

Currently the app is only published on [pypi](https://pypi.org/project/fastanime/).
With the following extras available:

- standard -which installs all dependencies
- api - which installs dependencies required to use `fastanime serve`
- mpv - which installs python mpv
- notifications - which installs plyer required for desktop notifications
  
#### Using uv

Recommended method of installation is using [uv](https://docs.astral.sh/uv/).

```bash
# generally:
uv tool install "fastanime[standard]"

# or stripped down installations:
uv tool install fastanime
uv tool install "fastanime[api]"
uv tool install "fastanime[mpv]"
uv tool install "fastanime[notifications]"

```

#### Using pipx

```bash

pipx install fastanime
# -- or for the development version --
pipx install 'fastanime==<latest-pre-release-tag>.dev1'
# example
# pipx install 'fastanime==0.60.1.dev1'

```

#### Using pip

```bash
pip install fastanime
# -- or for the development version --
pip install 'fastanime==<latest-pre-release-tag>.dev1'
# example
# pip install 'fastanime==0.60.1.dev1'
```

### Installing the bleeding edge version

To install the latest build which are created on every push by GitHub actions, download the [fastanime_debug_build](https://github.com/FastAnime/FastAnime/actions) of your choosing from the GitHub actions page.
Then:

```bash
unzip fastanime_debug_build

# outputs fastanime<version>.tar.gz

pipx install fastanime<version>.tar.gz

# --- or ---

pip install fastanime<version>.tar.gz
```

### Building from the source

Requirements:

- [git](https://git-scm.com/)
- [python 3.10 and above](https://www.python.org/)
- [uv](https://astral.sh/blog/uv)

To build from the source, follow these steps:

1. Clone the repository: `git clone https://github.com/Benexl/FastAnime.git --depth 1`
2. Navigate into the folder: `cd FastAnime`
3. Then build and Install the app:

```bash
# build and install fastanime with uv
uv tool install .
```

4. Enjoy! Verify installation with:

```bash
fastanime --version
```

> [!Tip]
>
> Download the completions from [here](https://github.com/FastAnime/FastAnime/tree/master/completions) for your shell.
> To add completions:
>
> - Fish Users: `cp $FASTANIME_PATH/completions/fastanime.fish ~/.config/fish/completions/`
> - Bash Users: Add `source $FASTANIME_PATH/completions/fastanime.bash` to your `.bashrc`
> - Zsh Users: Add `source $FASTANIME_PATH/completions/fastanime.zsh` to your `.zshrc`
>   or using the built in command `fastanime completions`

### External Dependencies

The only required external dependency, unless you won't be streaming, is [MPV](https://mpv.io/installation/), which i recommend installing with [uosc](https://github.com/tomasklaen/uosc) :fire: and [thumbfast](https://github.com/po5/thumbfast) for the best experience since they add a better interface to it.

> [!NOTE]
>
> The project currently sees no reason to support any other video
> player because we believe nothing beats **MPV** and it provides
> everything you could ever need with a small footprint.
> But if you have a reason feel free to encourage as to do so.
> However, on android this is not the case so vlc is also supported

**Other external dependencies that will just make your experience better:**

- [webtorrent-cli](https://github.com/webtorrent/webtorrent-cli) used when the provider is nyaa
- [ffmpeg](https://www.ffmpeg.org/) is required to be in your path environment variables to properly download [hls](https://www.cloudflare.com/en-gb/learning/video/what-is-http-live-streaming/) streams.
- [fzf](https://github.com/junegunn/fzf) 🔥 which is used as a better alternative to the ui.
- [rofi](https://github.com/davatorium/rofi) 🔥 which is used as another alternative ui + the desktop entry ui
- [chafa](https://github.com/hpjansson/chafa) currently the best cross platform and cross terminal image viewer for the terminal.
- [icat](https://sw.kovidgoyal.net/kitty/kittens/icat/) an image viewer that only works in [kitty terminal](https://sw.kovidgoyal.net/kitty/), which is currently the best terminal in my opinion, and by far the best image renderer for the terminal thanks to kitty's terminal graphics protocol. Its terminal graphics is so op that you can [run a browser on it](https://github.com/chase/awrit?tab=readme-ov-file)!!
- [bash](https://www.gnu.org/software/bash/) is used as the preview script language.
- [ani-skip](https://github.com/synacktraa/ani-skip) used for skipping the opening and ending theme songs
- [ffmpegthumbnailer](https://github.com/dirkvdb/ffmpegthumbnailer) used for local previews of downloaded anime
- [syncplay](https://syncplay.pl/) to enable watch together.
- [feh](https://github.com/derf/feh) used in manga mode
  
## Contributing

pr's are highly welcome

If you find an anime title that does not correspond with a provider or is just weird just [edit the data file](https://github.com/Benexl/FastAnime/blob/master/fastanime/Utility/data.py) and open a pr, issues will be ignored 😝.

## Supporting the Project

More pr's less issues 🙃

Show your support by starring the GitHub repository.

## Disclaimer

> [!IMPORTANT]
>
> This project currently scrapes allanime, hianime, nyaa, yugen and animepahe.
> The developer(s) of this application does not have any affiliation with the content providers available, and this application hosts zero content.
> [DISCLAIMER](https://github.com/Benexl/FastAnime/blob/master/DISCLAIMER.md)
