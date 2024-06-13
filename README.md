# Fast Anime

Welcome to Fast Anime, your new favorite destination for streaming and downloading anime.

![Preview Video Placeholder](https://github.com/Benex254/FastAnime/blob/master/.assets/screencasts/fastanime_demo.webm)

## Table of Contents

- [Installation](#installation)
  - [Using pip](#using-pip)
  - [Using pipx](#using-pipx)
  - [Pre-built binaries](#pre-built-binaries)
  - [Building from the source](#building-from-the-source)
- [Major Dependencies](#major-dependencies)
- [Contributing](#contributing)
- [Receiving Support](#receiving-support)
- [Supporting the Project](#supporting-the-project)

## Installation

### Using pip

Fast Anime can be installed using pip with the following command:

```bash
pip install <package-name>
#then you can launch the app using the following command:
python -m fastanime
```

> [!TIP]
> To add a desktop entry, execute the following command:
>
> ```bash
> python -m fastanime.ensure_desktop_icon
> ```

### Using pipx

Currently, this method is not functional. Please use the pip installation method instead.

### Pre-built binaries

We will soon release pre-built binaries for Linux and Windows.

### Building from the source

To build from the source, follow these steps:

1. Clone the repository: `git clone https://github.com/Benex254/FastAnime.git`
2. Navigate into the folder: `cd FastAnime`
3. create the virtual environment: `python -m venv .venv`
4. Activate the virtual environment: `source .venv/bin/activate` or on windows `.venv/scripts/activate`
5. Install dependencies: `pip install -r requirements.txt`
6. Build the app with: `python -m build`; ensure build is installed first.
7. Navigate to the dist folder: `cd dist`
8. Install the app with: `pip install fastanime-0.2.0-py3-none-any.whl`

## Major Dependencies

- Kivy and KivyMD for the UI
- PyShortcuts for creating a desktop icon
- FuzzyWuzzy for auto-selecting search results from the provider

## Contributing

We welcome your issues and feature requests. However, we currently have no plans to add another provider, so issues related to this may not be addressed due to time constraints. If you wish to contribute directly, please open an issue detailing the changes you wish to add and request a PR.

## Receiving Support

If you have any inquiries, join our Discord server: `<Discord-server-link>`

## Supporting the Project

If you want to support the project, please consider leaving a star on our GitHub repository or [buying us a coffee](ko-fi.com/benex254). We appreciate both!
