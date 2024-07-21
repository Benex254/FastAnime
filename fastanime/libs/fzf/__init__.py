import logging
import os
import shutil
import subprocess
import sys
from typing import Callable, List

from art import text2art
from rich import print

from ... import PLATFORM
from .config import FZF_DEFAULT_OPTS, FzfOptions

logger = logging.getLogger(__name__)


# fzf\
#   --info=hidden \
#   --layout=reverse \
#   --height=100% \
#   --prompt="Select Channel: " \
#   --header="$fzf_header" \
#   --preview-window=left,50%\
#   --bind=right:accept \
#   --expect=shift-left,shift-right\
#   --tabstop=1 \
#   --no-margin  \
#   +m \
#   -i \
#   --exact \


def clear():
    if PLATFORM == "Windows":
        os.system("cls")
    else:
        os.system("clear")


class FZF:
    if not os.getenv("FZF_DEFAULT_OPTS"):
        os.environ["FZF_DEFAULT_OPTS"] = FZF_DEFAULT_OPTS
    FZF_EXECUTABLE = shutil.which("fzf")
    default_options = [
        "--cycle",
        "--info=hidden",
        "--layout=reverse",
        "--height=100%",
        "--bind=right:accept",
        "--no-margin",
        "+m",
        "-i",
        "--exact",
        "--tabstop=1",
        "--preview-window=left,35%,wrap",
        "--wrap",
    ]

    def _with_filter(self, command: str, work: Callable) -> List[str]:
        try:
            process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                text=True,
                shell=True,
            )
        except subprocess.SubprocessError as e:
            print(f"Failed to start subprocess: {e}", file=sys.stderr)
            return []

        original_stdout = sys.stdout
        sys.stdout = process.stdin

        try:
            work()
            if process.stdin:
                process.stdin.close()
        except Exception as e:
            print(f"Exception during work execution: {e}", file=sys.stderr)
        finally:
            sys.stdout = original_stdout

        output = []
        if process.stdout:
            output = process.stdout.read().splitlines()
            process.stdout.close()

        return output

    def _run_fzf(self, commands: list[FzfOptions], _fzf_input) -> str:
        fzf_input = "\n".join(_fzf_input)

        if not self.FZF_EXECUTABLE:
            raise Exception("fzf executable not found")

        result = subprocess.run(
            [self.FZF_EXECUTABLE, *commands],
            input=fzf_input,
            stdout=subprocess.PIPE,
            text=True,
        )
        if not result or result.returncode != 0 or not result.stdout:
            print("sth went wrong:confused:")
            input("press enter to try again...")
            clear()
            return self._run_fzf(commands, _fzf_input)
        clear()

        return result.stdout.strip()

    def run(
        self,
        fzf_input: list[str],
        prompt: str,
        header: str,
        preview: str | None = None,
        expect: str | None = None,
        validator: Callable | None = None,
    ) -> str:
        _commands = [
            *self.default_options,
            "--header",
            text2art(header),
            "--header-first",
            "--prompt",
            prompt.title(),
        ]  # pyright:ignore

        if preview:
            _commands.append(f"--preview={preview}")
        if expect:
            _commands.append(f"--expect={expect}")

        result = self._run_fzf(_commands, fzf_input)  # pyright:ignore
        if not result:
            print("Please enter a value")
            input("Enter to do it right")
            return self.run(fzf_input, prompt, header, preview, expect, validator)
        elif validator:
            success, info = validator(result)
            if not success:
                print(info)
                input("Enter to try again")
                return self.run(fzf_input, prompt, header, preview, expect, validator)
        return result


fzf = FZF()

if __name__ == "__main__":
    fzf.run([*os.listdir(), "exit"], "Prompt: ", "Header", preview="bat {}")
