from kivy.properties import ObjectProperty, StringProperty

from View.base_screen import BaseScreenView
from Utility.kivy_markup_helper import bolden, color_text, underline
from Utility.data import themes_available

class HelpScreenView(BaseScreenView):
    main_container = ObjectProperty()
    animdl_help = StringProperty()
    installing_animdl_help = StringProperty()
    available_themes = StringProperty()
    def __init__(self, **kw):
        super(HelpScreenView, self).__init__(**kw)
        self.animdl_help = f"""
{underline(color_text(bolden('Streaming Commands'),self.theme_cls.surfaceBrightColor))}
    {color_text(bolden('-r:'),self.theme_cls.primaryFixedDimColor)} specifies the range of episodes
        example: {color_text(('animdl stream <Anime title> -r 1-4'),self.theme_cls.tertiaryColor)}
            explanation:in this case gets 4 episodes 1 to 4
    {color_text(('-s:'),self.theme_cls.primaryFixedDimColor)} special selector for the most recent episodes or basically selects from the end
        example: {color_text(('animdl stream <Anime title> -s 4'),self.theme_cls.tertiaryColor)}
            explanation: in this case gets the latest 4 episodes
    {color_text(('-q:'),self.theme_cls.primaryFixedDimColor)} sets the quality of the stream
        example: {color_text(('animdl stream <Anime title> -q best'),self.theme_cls.tertiaryColor)}
            explanation: The quality of the anime stream should be the best possible others include 1080,720... plus worst
{underline(color_text(bolden('Downloading Commands'),self.theme_cls.surfaceBrightColor))}
    {color_text(bolden('-r:'),self.theme_cls.primaryFixedDimColor)} specifies the range of episodes
        example: {color_text(('animdl download <Anime title> -r 1-4'),self.theme_cls.tertiaryColor)}
            explanation:in this case gets 4 episodes 1 to 4
    {color_text(('-s:'),self.theme_cls.primaryFixedDimColor)} special selector for the most recent episodes or basically selects from the end
        example: {color_text(('animdl download <Anime title> -s 4'),self.theme_cls.tertiaryColor)}
            explanation: in this case gets the latest 4 episodes
    {color_text(('-q:'),self.theme_cls.primaryFixedDimColor)} sets the quality of the download
        example: {color_text(('animdl download <Anime title> -q best'),self.theme_cls.tertiaryColor)}
            explanation: The quality of the anime download should be the best possible others include 1080,720... plus worst
            """
        self.installing_animdl_help = f"""
This works on windows only and should be done in powershell
1. First install pyenv with the following command:
{color_text(('Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"'),self.theme_cls.tertiaryColor)}
2. run the following command to check if successsful:
{color_text(('pyenv --version '),self.theme_cls.tertiaryColor)}
3.  run the following command to install python 3.10
{color_text(('pyenv install 3.10'),self.theme_cls.tertiaryColor)}
4. To confirm successful install of python 3.10 run the following command and check if 3.10 is listed:
{color_text(('pyenv -l'),self.theme_cls.tertiaryColor)}
5. Next run: 
{color_text(('pyenv local 3.10'),self.theme_cls.tertiaryColor)} (if in anixstream directory to set python 3.10 as local interpreter)
or run:
{color_text(('pyenv global 3.10'),self.theme_cls.tertiaryColor)} (if in another directory to set python version 3.10 as global interpreter) 
6. Check if success by running and checking if output is 3.10: 
{color_text(('python --version'),self.theme_cls.tertiaryColor)}
7. Run:
{color_text(('python -m pip install animdl'),self.theme_cls.tertiaryColor)}
8. Check if success by running:
{color_text(('python -m animdl'),self.theme_cls.tertiaryColor)} 
{color_text(('Note:'),self.theme_cls.secondaryColor)}
All this instructions should be done from the folder you choose to install
aniXstream but incase you have never installed python should work any where
{bolden('-----------------------------')}
Now enjoy :)
{bolden('-----------------------------')}
            """
        self.available_themes = "\n".join(themes_available)

    def model_is_changed(self) -> None:
        """
        Called whenever any change has occurred in the data model.
        The view in this method tracks these changes and updates the UI
        according to these changes.
        """
