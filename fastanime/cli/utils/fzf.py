import subprocess
import logging

logger = logging.getLogger(__name__)


def run_fzf(options: tuple[str], *custom_commands):
    """
    Run fzf with a list of options and return the selected option.
    """
    # Join the list of options into a single string with newlines
    options_str = "\n".join(options)

    # Run fzf as a subprocess
    result = subprocess.run(
        ["fzf", *custom_commands],
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
