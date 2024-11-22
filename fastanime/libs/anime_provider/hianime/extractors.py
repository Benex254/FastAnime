import requests
import time
import re
import json
from typing import List, Dict
from Crypto.Cipher import AES
from Crypto.Hash import MD5

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


class MegaCloud:
    def extract(self, video_url: str) -> Dict:
        try:
            extracted_data = {
                "tracks": [],
                "intro": {"start": 0, "end": 0},
                "outro": {"start": 0, "end": 0},
                "sources": [],
            }

            video_id = video_url.split("/")[-1].split("?")[0]
            response = requests.get(
                megacloud["sources"] + video_id,
                headers={
                    "Accept": "*/*",
                    "X-Requested-With": "XMLHttpRequest",
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
                    ),
                    "Referer": video_url,
                },
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
            script_response = requests.get(
                megacloud["script"] + str(int(time.time() * 1000))
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
    ) -> Dict[str, str]:
        secret = []
        encrypted_source_array = list(encrypted_string)
        current_index = 0

        for start, length in values:
            start += current_index
            end = start + length
            secret.extend(encrypted_string[start:end])
            encrypted_source_array[start:end] = [""] * length
            current_index += length

        encrypted_source = "".join(encrypted_source_array).replace("\x00", "")
        return {"secret": "".join(secret), "encrypted_source": encrypted_source}

    def decrypt(self, encrypted: str, key_or_secret: str, maybe_iv: str = "") -> str:
        if maybe_iv:
            key, iv, contents = key_or_secret.encode(), maybe_iv.encode(), encrypted
        else:
            # Handle OpenSSL key derivation
            print(encrypted)
            input()
            cypher = bytes.fromhex(encrypted)
            salt = cypher[8:16]
            password = key_or_secret.encode() + salt

            md5_hashes = []
            for _ in range(3):
                md5 = MD5.new()
                md5.update(password)
                md5_hash = md5.digest()
                md5_hashes.append(md5_hash)
                password = md5_hash + password

            key = md5_hashes[0] + md5_hashes[1]
            iv = md5_hashes[2]
            contents = cypher[16:]

        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(contents)

        # Remove padding
        pad_len = decrypted[-1]
        return decrypted[:-pad_len].decode("utf-8")

    def matching_key(self, value: str, script: str) -> str:
        match = re.search(rf",{value}=((?:0x)?[0-9a-fA-F]+)", script)
        if match:
            return match.group(1).replace("0x", "")
        raise Exception("Failed to match the key")
