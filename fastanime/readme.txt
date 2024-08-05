All this instructions should be done from the folder you chose to install
aniXstream but incase you have never installed python should work any where

1. First install pyenv with the following command:
Invoke-WebRequest -UseBasicParsing -Uri
"https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1"
-OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"
2. run the following command:
 pyenv --version to check whether installation was a success
3.  run  pyenv install 3.10 and confirm success by running  pyenv -l and check
for 3.10
4. run pyenv local 3.10 (if in anixstream directory) or pyenv global 3.10 (if
in another directory to set python version 3.10 as global interpreter) 
5. check if success by running python --version and checking if output is 3.10
6. run python -m pip install animdl
7. check if success by running python -m animdl and if no error then you are
ready to use anixstream to stream anime
8. additionally you can use animdl independently by running python -m animdl
and any arguments specified in the animdl documentation eg python -m animdl
stream naruto
-----------------------------
Now enjoy :)
------------------------------
