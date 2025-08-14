from typing import Protocol, Mapping, Any
import random


class Provider(Protocol):
    name: str

    def generate(self, rng: random.Random, overrides: Mapping[str, Any]) -> Any: ...
