from typing import Mapping, Any
import random
import string


class TokenProvider:
    name = "token"

    def generate(self, rng: random.Random, overrides: Mapping[str, Any]) -> str:
        """
        Defaults:
          length = overrides.get("length", 32)
          charset = overrides.get("charset", string.ascii_letters + string.digits)
        Use rng.choices(charset, k=length).
        """
        ...
