from typing import Mapping, Any
import random
import string
from ..policies.password_policy import PasswordPolicy


class PasswordProvider:
    name = "password"

    def __init__(self, default_policy: PasswordPolicy | None = None) -> None: ...

    def generate(self, rng: random.Random, overrides: Mapping[str, Any]) -> str:
        """
        Algorithm outline you’ll implement:
          1) Merge default_policy with overrides to create a PasswordPolicy instance.
          2) policy.validate()
          3) length, nU, nD, nS, specials = policy.effective_counts()
          4) Build a list of required chars:
               - nU uppercase from A-Z
               - nD digits 0-9
               - nS specials from specials
             Fill the remainder with lowercase a-z.
          5) Shuffle with rng and return as string.
        """
        ...
