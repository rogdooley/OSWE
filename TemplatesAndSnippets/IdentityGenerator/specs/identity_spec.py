from typing import Mapping, Any, FrozenSet, Optional
from dataclasses import dataclass, field
from ..policies.password_policy import PasswordPolicy


@dataclass(frozen=True)
class IdentitySpec:
    domain: Optional[str] = None
    username_format: str = "{first}_{last}{##}"
    email_format: str = "{first}.{last}{##}"
    password: PasswordPolicy = field(default_factory=PasswordPolicy)
    include_uuid: bool = True
    include_token: bool = True
    extras: FrozenSet[str] = frozenset()
    overrides: Mapping[str, Mapping[str, Any]] = field(default_factory=dict)
    profile_name: str = "standard"


def make_minimal_spec(**kw) -> IdentitySpec: ...
def make_standard_spec(**kw) -> IdentitySpec: ...
def make_us_contact_spec(**kw) -> IdentitySpec:
    # Set extras={"address","phone"} later when those providers exist
    ...
