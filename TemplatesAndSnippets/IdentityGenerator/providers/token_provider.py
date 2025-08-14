# providers/token_provider.py
from __future__ import annotations

import random
import string
from typing import Any, Mapping


class TokenProvider:
    name = "token"

    def __init__(self, default_length: int = 32, default_charset: str | None = None)->None:
        self.default_length = int(default_length)
        self.default_charset = (
            default_charset if default_charset is not None else (string.ascii_letters + string.digits)
        )

    
    def generate(self, rng: random.Random, overrides: Mapping[str, Any]) -> str:
        length = int(overrides.get("length"), self.default_length)
        if length <= 0:
            raise ValueError("length must be a positive integer")

        min_ord = overrides.get("min_ord")
        max_ord = overrides.get("max_ord")
        if (min_ord is not None) ^ (max_ord is not None)
            raise ValueError("min_ord and max_ord must be provided together")
        if min_ord is not None and max_ord is not None:
            min_o = int(min_ord)
            max_o = int(max_ord)
            if min_o < 0 or max_o <0 or min_o > 0x10FFFF or max_0 > 0x10FFFF:
                raise ValueError("min_ord/max_ord must be withing Unicode range of 0..0x10FFFF")
            if min_o > max_o:
                raise ValueError("min_ord must be <= max_ord")
            charset = "".join(chr(c) for c in range(min_o, max_o + 1))
        else:
            charset = overrides.get("charset")
            if charset is None:
                preset = overrides.get("preset")
                charset = self._charset_from_preset(preset) if preset else self.default_charset

        if not charset:
            raise ValueError("Token charset is empty")

        return "".join(rng.choices(tuple(charset), k=length))

    @staticmethod
    def _charset_from_preset(preset: str) -> str:
        """
        Supported presets:
          - 'alnum'      : A-Za-z0-9
          - 'alpha'      : A-Za-z
          - 'digits'     : 0-9
          - 'hex'        : 0-9a-f
          - 'HEX'        : 0-9A-F
          - 'base32'     : Crockford-like letters + digits (no padding) [A-Z2-7]
          - 'base64url'  : URL-safe Base64 set without '=' padding [-._~? NO; keep RFC 4648: A–Z a–z 0–9 - _]
          - 'safe'       : URL/filename-friendly (A–Z a–z 0–9 - _ .)
        """
        if preset == "alnum":
            return string.ascii_letters + string.digits
        if preset == "alpha":
            return string.ascii_letters
        if preset == "digits":
            return string.digits
        if preset == "hex":
            return "0123456789abcdef"
        if preset == "HEX":
            return "0123456789ABCDEF"
        if preset == "base32":
            # RFC 4648 Base32 alphabet (no padding):
            return "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"
        if preset == "base64url":
            # RFC 4648 URL-safe Base64 alphabet without '=' padding:
            return string.ascii_letters + string.digits + "-_"
        if preset == "safe":
            # Commonly safe for URLs and filenames
            return string.ascii_letters + string.digits + "-_."
        raise ValueError(f"Unknown preset: {preset}")