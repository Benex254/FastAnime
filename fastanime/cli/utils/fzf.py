import subprocess
import logging
import shutil

logger = logging.getLogger(__name__)


def fzf(options, prompt="Select Anime: ", *custom_commands):
    """
    Run fzf with a list of options and return the selected option.
    """
    # Join the list of options into a single string with newlines
    options_str = "\n".join(options)

    # Run fzf as a subprocess
    FZF = shutil.which("fzf")
    if not FZF:
        logger.error("fzf not found")
        return None

    result = subprocess.run(
        [
            FZF,
            "--reverse",
            "--cycle",
            "--prompt",
            prompt,
        ]
        if not custom_commands
        else [FZF, *custom_commands],
        input=options_str,
        text=True,
        stdout=subprocess.PIPE,
    )

    # Check if fzf was successful
    if result.returncode == 0:
        # Return the selected option
        selection = result.stdout.strip()
        logger.info(f"fzf: selected {selection}")
        return selection
    else:
        # Handle the case where fzf fails or is canceled
        logger.error("fzf was canceled or failed")
        return None
