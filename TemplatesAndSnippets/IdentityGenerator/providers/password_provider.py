import random
import string

from typing import Mapping, Any, Literal, Optional

Complexity = Literal["low", "medium", "high"]

COMPLEXITY_MIN_LENGTH: dict[Complexity, int] = {
    "low": 12,
    "medium": 16,
    "high": 20,
}

COMPLEXITY_MIN_COUNTS: dict[Complexity, tuple[int, int, int]] = {
    "low": (1, 1, 0),
    "medium": (2, 2, 1),
    "high": (3, 3, 2),
}

DEFAULT_SPECIALS = "!@#$%^&*()-_=+{}[]"


class PasswordProvider:
    name = "password"

    def __init__(
        self,
        *,
        length: int = 16,
        complexity: Optional[Complexity] = "medium",
        num_upper: Optional[int] = None,
        num_digits: Optional[int] = None,
        num_special: Optional[int] = None,
        special_chars: str = DEFAULT_SPECIALS,
    ) -> None:
        self.length = length
        self.complexity = complexity
        self.num_upper = num_upper
        self.num_digits = num_digits
        self.num_special = num_special
        self.special_chars = special_chars

    def validate(self) -> None:
        """
        Checks that the policy parameters are internally consistent.
        Raises ValueError if something is invalid.
        """
        if self.length <= 0:
            raise ValueError("Password length must be greater than zero")

        for label, value in (
            ("num_upper", self.num_upper),
            ("num_digits", self.num_digits),
            ("num_special", self.num_special),
        ):
            if value is not None and value < 0:
                raise ValueError(f"{label} must be >= 0")

        if (self.num_special and self.num_special > 0) and not self.special_chars:
            raise ValueError("special_chars cannot be empty when num_special > 0.")

        if self.complexity is not None and self.complexity not in COMPLEXITY_MIN_LENGTH:
            raise ValueError(f"Unknown complexity level: {self.complexity}")

    def effective_counts(self) -> tuple[int, int, int, int, str]:
        if self.complexity:
            min_length_for_complexity = COMPLEXITY_MIN_LENGTH[self.complexity]
            counts = COMPLEXITY_MIN_COUNTS[self.complexity]
        else:
            min_length_for_complexity = 0
            counts = (0, 0, 0)

        length = max(self.length, min_length_for_complexity)
        num_upper, num_digits, num_special = counts

        if self.num_upper is not None:
            num_upper = self.num_upper
        if self.num_digits is not None:
            num_digits = self.num_digits
        if self.num_special is not None:
            num_special = self.num_special

        required_length = num_upper + num_digits + num_special

        if required_length > length:
            raise ValueError("Sum of character class counts exceeds password length.")

        return (length, num_upper, num_digits, num_special, self.special_chars)

    def generate(self, rng: random.Random, overrides: dict) -> str:
        """
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

        temp = PasswordProvider(
            length=overrides.get("length", self.length),
            complexity=overrides.get("complexity", self.complexity),
            num_upper=overrides.get("num_upper", self.num_upper),
            num_digits=overrides.get("num_digits", self.num_digits),
            num_special=overrides.get("num_special", self.num_special),
            special_chars=overrides.get("special_chars", self.special_chars),
        )

        temp.validate()

        length, num_upper, num_digits, num_special, special_chars = (
            temp.effective_counts()
        )

        chars = []
        chars += [rng.choice(string.ascii_uppercase) for _ in range(num_upper)]
        chars += [rng.choice(string.digits) for _ in range(num_digits)]
        chars += [rng.choice(special_chars) for _ in range(num_special)]
        chars += [
            rng.choice(string.ascii_lowercase) for _ in range(length - len(chars))
        ]

        rng.shuffle(chars)
        return "".join(chars)
