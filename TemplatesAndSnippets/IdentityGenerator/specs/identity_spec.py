from typing import Optional


class IdentitySpec:
    def __init__(
        self,
        domain: Optional[str] = None,
        username_format: str = "{first}_{last}{##}",
        email_format: str = "{first}.{last}{##}",
        include_uuid: bool = True,
        include_token: bool = True,
        extras: Optional[list[str]] = None,
        overrides: Optional[dict[str, dict]] = None,
    ):
        self.domain = domain
        self.username_format = username_format
        self.email_format = email_format
        self.include_uuid = include_uuid
        self.include_token = include_token
        self.extras = extras or []
        self.overrides = overrides or {}
