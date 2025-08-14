from typing import Literal, Optional

Complexity = Literal["low", "medium", "high"]


class IdentitySpec:
    def __init__(
        self,
        domain: Optional[str] = None,
        username_format: str = "{first}{last}",
        email_format: str = "{first}.{last}",
        include_token: bool = False,
        extras: Optional[list[str]] = None,
        overrides: Optional[dict] = None,
    ):
        self.domain = domain
        self.username_format = username_format
        self.email_format = email_format
        self.include_token = include_token
        self.extras = extras or []  # e.g., ["address", "phone"]
        self.overrides = overrides or {}

    def wants(self, feature: str) -> bool:
        """Check if the feature is requested in extras."""
        return feature in self.extras
