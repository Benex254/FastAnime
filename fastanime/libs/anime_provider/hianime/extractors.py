import hashlib
import json
import re
import time
from base64 import b64decode
from typing import TYPE_CHECKING, Dict, List

from Crypto.Cipher import AES

if TYPE_CHECKING:
    from ...common.requests_cacher import CachedRequestsSession


# Constants
megacloud = {
    "script": "https://megacloud.tv/js/player/a/prod/e1-player.min.js?v=",
    "sources": "https://megacloud.tv/embed-2/ajax/e-1/getSources?id=",
}


class HiAnimeError(Exception):
    def __init__(self, message, context, status_code):
        super().__init__(f"{context}: {message} (Status: {status_code})")
        self.context = context
        self.status_code = status_code


# Adapted from https://github.com/ghoshRitesh12/aniwatch
class MegaCloud:
    def __init__(self, session):
        self.session: "CachedRequestsSession" = session

    def extract(self, video_url: str) -> Dict:
        try:
            extracted_data = {
                "tracks": [],
                "intro": {"start": 0, "end": 0},
                "outro": {"start": 0, "end": 0},
                "sources": [],
            }

            video_id = video_url.split("/")[-1].split("?")[0]
            response = self.session.get(
                megacloud["sources"] + video_id,
                headers={
                    "Accept": "*/*",
                    "X-Requested-With": "XMLHttpRequest",
                    "Referer": video_url,
                },
                fresh=1,  # pyright: ignore
            )
            srcs_data = response.json()

            if not srcs_data:
                raise HiAnimeError(
                    "Url may have an invalid video id", "getAnimeEpisodeSources", 400
                )

            encrypted_string = srcs_data["sources"]
            if not srcs_data["encrypted"] and isinstance(encrypted_string, list):
                extracted_data.update(
                    {
                        "intro": srcs_data["intro"],
                        "outro": srcs_data["outro"],
                        "tracks": srcs_data["tracks"],
                        "sources": [
                            {"url": s["file"], "type": s["type"]}
                            for s in encrypted_string
                        ],
                    }
                )
                return extracted_data

            # Fetch decryption script
            script_response = self.session.get(
                megacloud["script"] + str(int(time.time() * 1000)),
                fresh=1,  # pyright: ignore
            )
            script_text = script_response.text
            if not script_text:
                raise HiAnimeError(
                    "Couldn't fetch script to decrypt resource",
                    "getAnimeEpisodeSources",
                    500,
                )

            vars_ = self.extract_variables(script_text)
            if not vars_:
                raise Exception(
                    "Can't find variables. Perhaps the extractor is outdated."
                )

            secret, encrypted_source = self.get_secret(encrypted_string, vars_)
            decrypted = self.decrypt(encrypted_source, secret)

            try:
                sources = json.loads(decrypted)
                extracted_data.update(
                    {
                        "intro": srcs_data["intro"],
                        "outro": srcs_data["outro"],
                        "tracks": srcs_data["tracks"],
                        "sources": [
                            {"url": s["file"], "type": s["type"]} for s in sources
                        ],
                    }
                )
                return extracted_data
            except Exception:
                raise HiAnimeError(
                    "Failed to decrypt resource", "getAnimeEpisodeSources", 500
                )
        except Exception as err:
            raise err

    def extract_variables(self, text: str) -> List[List[int]]:
        regex = r"case\s*0x[0-9a-f]+:(?![^;]*=partKey)\s*\w+\s*=\s*(\w+)\s*,\s*\w+\s*=\s*(\w+);"
        matches = re.finditer(regex, text)
        vars_ = []
        for match in matches:
            key1 = self.matching_key(match[1], text)
            key2 = self.matching_key(match[2], text)
            try:
                vars_.append([int(key1, 16), int(key2, 16)])
            except ValueError:
                continue
        return vars_

    def get_secret(
        self, encrypted_string: str, values: List[List[int]]
    ) -> tuple[str, str]:
        secret = []
        encrypted_source_array = list(encrypted_string)
        current_index = 0

        for start, length in values:
            start += current_index
            end = start + length
            secret.extend(encrypted_string[start:end])
            encrypted_source_array[start:end] = [""] * length
            current_index += length

        encrypted_source = "".join(encrypted_source_array)  # .replace("\x00", "")
        return ("".join(secret), encrypted_source)

    def decrypt(self, encrypted: str, key_or_secret: str, maybe_iv: str = "") -> str:
        if maybe_iv:
            key = key_or_secret.encode()
            iv = maybe_iv.encode()
            contents = encrypted
        else:
            # Decode the Base64 string
            cypher = b64decode(encrypted)

            # Extract the salt from the cypher text
            salt = cypher[8:16]

            # Combine the key_or_secret with the salt
            password = key_or_secret.encode() + salt

            # Generate MD5 hashes
            md5_hashes = []
            digest = password
            for _ in range(3):
                md5 = hashlib.md5()
                md5.update(digest)
                md5_hashes.append(md5.digest())
                digest = md5_hashes[-1] + password

            # Derive the key and IV
            key = md5_hashes[0] + md5_hashes[1]
            iv = md5_hashes[2]

            # Extract the encrypted contents
            contents = cypher[16:]

        # Initialize the AES decipher
        decipher = AES.new(key, AES.MODE_CBC, iv)

        # Decrypt and decode
        decrypted = decipher.decrypt(contents).decode("utf-8")  # pyright: ignore

        # Remove any padding (PKCS#7)
        pad = ord(decrypted[-1])
        return decrypted[:-pad]

    def matching_key(self, value: str, script: str) -> str:
        match = re.search(rf",{value}=((?:0x)?[0-9a-fA-F]+)", script)
        if match:
            return match.group(1).replace("0x", "")
        raise Exception("Failed to match the key")
