from typing import Literal, Optional

Complexity = Literal["low", "medium", "high"]


class PasswordPolicy:
    def __init__(
        self,
        *,
        length: int = 16,
        complexity: Optional[Complexity] = "medium",
        num_upper: Optional[int] = None,
        num_digits: Optional[int] = None,
        num_special: Optional[int] = None,
        special_chars: str = "!@#$%^&*()-_=+[]{}",
    ) -> None: ...

    def validate(self) -> None: ...
    def effective_counts(self) -> tuple[int, int, int, int, str]:
        """
        Returns (length, num_upper, num_digits, num_special, special_chars).
        Rules:
          - If complexity is set, map to minimum guarantees:
              low -> at least length 12, 1U/1D/0S
              medium -> at least length 16, 2U/2D/1S
              high -> at least length 20, 3U/3D/2S
          - If explicit counts provided, they override complexity guarantees.
          - Enforce sum(counts) <= length.
        """
        ...
