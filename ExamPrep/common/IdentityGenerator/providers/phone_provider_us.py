import random


class PhoneProviderUS:
    def generate(self, rng: random.Random, overrides: dict = {}) -> str:
        return (
            f"{rng.randint(100, 999)}-{rng.randint(100, 999)}-{rng.randint(1000, 9999)}"
        )
