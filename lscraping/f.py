import re


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


print(
    decode_hex_string(
        "175948514e4c4f57175b54575b5307515c050f5c0a0c0f0b0f0c0e590a0c0b5b0a0c0a010f0d0e5e0f0a0e0b0f0d0a010e0f0e000e5e0e5a0e0b0a010d0d0e5d0e0f0f0c0e0b0e0a0a0e0c0a0e010e0d0f0b0e5a0e0b0e000f0a0f0d0a010e000f0e0b090f5d0c5a0b0d0b0c0b0d0f080b0b0f0e0c5d0b080c5c0d5e0b5e0e0b0d010b0f0b0c0d010f0d0f0b0e0c0a000e5a0f0e0b0a0a0c0a590a0c0f0d0f0a0f0c0e0b0e0f0e5a0e0b0f0c0c5e0e0a0a0c0b5b0a0c0d0d0e5d0e0f0f0c0e0b0f0e0e010e5e0e000f0a0a0c0a590a0c0e0a0e0f0f0a0e0b0a0c0b5b0a0c0b0c0b0e0b0c0b0a0a5a0b0e0b080a5a0b0e0b090d0a0b0f0b5e0b5b0b0b0b5e0b5b0b0e0b0e0a000b0e0b0e0b0e0d5b0a0c0a590a0c0f0a0f0c0e0f0e000f0d0e590e0f0f0a0e5e0e010e000d0a0f5e0f0e0e0b0a0c0b5b0a0c0f0d0f0b0e0c0a0c0a590a0c0e5c0e0b0f5e0a0c0b5b0a0c0e0b0f0e0a5a0e000f0e0b090f5d0c5a0b0d0b0c0b0d0f080b0b0f0e0c5d0b080c5c0d5e0b5e0e0b0d010b0f0b0c0d010f0d0f0b0e0c0a0c0f5a"
    )
)
