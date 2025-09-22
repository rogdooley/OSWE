# utils.py

import base64
import urllib.parse
import json


def decode_b64(b64_string: str) -> str:
    try:
        if "," in b64_string:
            b64_string = b64_string.split(",", 1)[1]

        decoded_bytes = base64.b64decode(b64_string)
        return decoded_bytes.decode("utf-8", errors="replace")
    except Exception as e:
        return f"[Base64 decode failed] {e}"


def encode_b64(text: str) -> str:
    return base64.b64encode(text.encode("utf-8")).decode("utf-8")


def decode_hex(hex_string: str) -> str:
    try:
        decoded_bytes = bytes.fromhex(hex_string)
        return decoded_bytes.decode("utf-8", errors="replace")
    except Exception as e:
        return f"[Hex decode failed] {e}"


def encode_hex(text: str) -> str:
    return text.encode("utf-8").hex()


def decode_url(url_encoded: str) -> str:
    return urllib.parse.unquote(url_encoded)


def encode_url(text: str) -> str:
    return urllib.parse.quote(text)


def decode_jwt_payload(jwt_token: str) -> str:
    try:
        parts = jwt_token.split(".")
        if len(parts) != 3:
            return "[Invalid JWT format]"

        payload = parts[1]
        # Add padding if missing
        missing_padding = len(payload) % 4
        if missing_padding:
            payload += "=" * (4 - missing_padding)

        decoded_bytes = base64.urlsafe_b64decode(payload)
        json_data = json.loads(decoded_bytes)
        return json.dumps(json_data, indent=2)
    except Exception as e:
        return f"[JWT payload decode failed] {e}"
