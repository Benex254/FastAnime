import re
import subprocess

# Dictionary to map hex values to characters
hex_to_char = {
    "01": "9",
    "08": "0",
    "05": "=",
    "0a": "2",
    "0b": "3",
    "0c": "4",
    "07": "?",
    "00": "8",
    "5c": "d",
    "0f": "7",
    "5e": "f",
    "17": "/",
    "54": "l",
    "09": "1",
    "48": "p",
    "4f": "w",
    "0e": "6",
    "5b": "c",
    "5d": "e",
    "0d": "5",
    "53": "k",
    "1e": "&",
    "5a": "b",
    "59": "a",
    "4a": "r",
    "4c": "t",
    "4e": "v",
    "57": "o",
    "51": "i",
}


def decode_hex_string(hex_string):
    # Split the hex string into pairs of characters
    hex_pairs = re.findall("..", hex_string)

    # Decode each hex pair
    decoded_chars = [hex_to_char.get(pair.lower(), pair) for pair in hex_pairs]

    return "".join(decoded_chars)


def run_fzf(options):
    """
    Run fzf with a list of options and return the selected option.
    """
    # Join the list of options into a single string with newlines
    options_str = "\n".join(options)

    # Run fzf as a subprocess
    result = subprocess.run(
        ["fzf"],
        input=options_str,
        text=True,
        stdout=subprocess.PIPE,
    )

    # Check if fzf was successful
    if result.returncode == 0:
        # Return the selected option
        return result.stdout.strip()
    else:
        # Handle the case where fzf fails or is canceled
        print("fzf was canceled or failed")
        return None
