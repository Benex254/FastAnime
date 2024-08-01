import subprocess
from shutil import which
from sys import exit


class RofiApi:
    ROFI_EXECUTABLE = which("rofi")

    rofi_theme = ""

    def run_with_icons(self, options: list[str], prompt_text: str) -> str:
        rofi_input = "\n".join(options)

        if not self.ROFI_EXECUTABLE:
            raise Exception("Rofi not found")

        args = [self.ROFI_EXECUTABLE]
        if self.rofi_theme:
            args.extend(["-no-config", "-theme", self.rofi_theme])
        args.extend(["-p", prompt_text, "-i", "-show-icons", "-dmenu"])
        result = subprocess.run(
            args,
            input=rofi_input,
            stdout=subprocess.PIPE,
            text=True,
        )

        choice = result.stdout.strip()
        if not choice:
            exit(1)

        return choice

    def run(self, options: list[str], prompt_text: str) -> str:
        rofi_input = "\n".join(options)

        if not self.ROFI_EXECUTABLE:
            raise Exception("Rofi not found")

        args = [self.ROFI_EXECUTABLE]
        if self.rofi_theme:
            args.extend(["-no-config", "-theme", self.rofi_theme])
        args.extend(["-p", prompt_text, "-i", "-dmenu"])
        result = subprocess.run(
            args,
            input=rofi_input,
            stdout=subprocess.PIPE,
            text=True,
        )

        choice = result.stdout.strip()
        if not choice or choice not in options:
            exit(1)

        return choice


Rofi = RofiApi()
