import random
import string
import uuid
import json

from typing import Optional
from datetime import datetime, timezone

from .specs.identity_spec import IdentitySpec


class IdentityGenerator:
    """
    IdentityGenerator is a modular, extensible utility for generating realistic
    test identities for use in exploit development, CTFs, and automation workflows.

    Features:
        - Supports randomized and deterministic (seeded) identity generation
        - Extensible via pluggable data providers (username, password, address, phone, etc.)
        - Format-string support for custom username/email patterns
        - Fine-grained control via IdentitySpec or kwargs
        - Save/load identities as JSON for repeatable usage

    Core Methods:
        - generate_username(): Generate username from format (e.g., "{first}{last}{##}")
        - generate_email(): Generate email with format and domain
        - generate_password(): Generate password from complexity or explicit rules
        - generate_token(): Generate a random token
        - generate_uuid(): Generate a UUID4 string
        - generate_identity(): Main entry point for full identity generation
        - save_identity()/load_identity(): Persist generated identities to disk
        - as_dict()/as_json(): Export last identity in structured formats

    Usage:
        # Direct with kwargs
        >>> gen = IdentityGenerator()
        >>> identity = gen.generate_identity(
        ...     domain="corp.local",
        ...     username_format="f.lastname",
        ...     email_format="first.last##",
        ...     password_complexity="high",
        ...     include_token=True,

        ...     extras=["address", "phone"]
        ... )

        # Structured via IdentitySpec
        >>> from .specs.identity_spec import IdentitySpec
        >>> spec = IdentitySpec(
        ...     domain="corp.io",
        ...     username_format="first_last##",
        ...     email_format="f.lastname",
        ...     include_token=True,
        ...     extras=["address"],
        ...     overrides={"password": {"length": 20, "complexity": "medium"}}
        ... )
        >>> identity = gen.generate_identity(spec)
        >>> print(identity)

    """

    def __init__(self, seed: Optional[int] = None):
        self._rng = random.Random(seed)
        self._providers = {}
        self._register_default_providers()

        self.first_names = [
            "Alice",
            "Bob",
            "Charlie",
            "Diana",
            "Eve",
            "Frank",
            "Grace",
            "Heidi",
            "Ivan",
            "Judy",
            "Karl",
            "Laura",
            "Mallory",
            "Nina",
            "Oscar",
            "Peggy",
            "Quinn",
            "Ruth",
            "Steve",
            "Trudy",
        ]
        self.last_names = [
            "Anderson",
            "Baker",
            "Clark",
            "Davis",
            "Evans",
            "Foster",
            "Garcia",
            "Harris",
            "Iverson",
            "Johnson",
            "Knight",
            "Lewis",
            "Miller",
            "Nguyen",
            "Owens",
            "Perry",
            "Quinn",
            "Roberts",
            "Stewart",
            "Turner",
        ]
        self.default_domains = [
            "example.com",
            "testmail.org",
            "fakemail.net",
            "mailinator.com",
            "inbox.test",
            "demo.site",
            "mockdomain.co",
            "tempmail.dev",
            "sandbox.io",
            "fakeinbox.xyz",
        ]

    def _register_default_providers(self) -> None:
        from .providers.password_provider import PasswordProvider
        from .providers.token_provider import TokenProvider
        from .providers.address_provider_us import AddressProviderUS
        from .providers.phone_provider_us import PhoneProviderUS

        self._providers["password"] = PasswordProvider()
        self._providers["token"] = TokenProvider()
        self._providers["address"] = AddressProviderUS()
        self._providers["phone"] = PhoneProviderUS()

    def generate_username(self, format: str = "{first}{last}{##}") -> str:
        if not hasattr(self, "last_first_name") or not hasattr(self, "last_last_name"):
            self._generate_name()
        first, last = self.last_first_name.lower(), self.last_last_name.lower()
        number = str(self._rng.randint(10, 99))
        initial = first[0]

        placeholders = {"first": first, "last": last, "f": initial, "##": number}

        username = format

        for key, value in placeholders.items():
            username = username.replace(f"{{{key}}}", value)

        return username

    def generate_email(
        self, domain: Optional[str] = None, format: str = "{first}{last}{##}"
    ) -> str:
        if not hasattr(self, "last_first_name") or not hasattr(self, "last_last_name"):
            self._generate_name()
        first = self.last_first_name.lower()
        last = self.last_last_name.lower()
        number = str(self._rng.randint(10, 99))
        initial = first[0]
        domain = domain or self._rng.choice(self.default_domains)

        placeholders = {"first": first, "last": last, "f": initial, "##": number}

        email_local = format
        for key, value in placeholders.items():
            email_local = email_local.replace(f"{{{key}}}", value)

        return f"{email_local}@{domain}"

    def _generate_with_spec(self, spec: IdentitySpec) -> dict:
        """
        Internal: Generates and identity from a fully built IdentitySpec.
        Uses providers for password/token and exisiting logic for name, username, email.
        """
        self._generate_name()

        identity = {
            "first_name": self.last_first_name,
            "last_name": self.last_last_name,
            "username": self.generate_username(spec.username_format),
            "email": self.generate_email(spec.domain, spec.email_format),
        }

        # Password via provider
        identity["password"] = self._providers["password"].generate(
            self._rng, spec.overrides.get("password", {})
        )

        # Timestamp
        identity["created_at"] = datetime.now(timezone.utc).isoformat()

        # Optional fields
        if spec.include_token:
            identity["token"] = self._providers["token"].generate(
                self._rng, spec.overrides.get("token", {})
            )

        # Extras (future: address, phone, etc.)
        for extra in spec.extras:
            if extra in self._providers:
                identity[extra] = self._providers[extra].generate(
                    self._rng, spec.overrides.get(extra, {})
                )

        # Remember last identity
        self.last_identity = identity
        return identity

    def generate_password(
        self,
        length: int = 12,
        num_upper: Optional[int] = None,
        num_digits: Optional[int] = None,
        num_special: Optional[int] = None,
        special_chars: str = "!@#$%^&*()-_=+[]{}",
        complexity: Optional[str] = None,
    ) -> str:
        # If no complexity is given and no explicit values, fallback
        if complexity and any([num_upper, num_digits, num_special]):
            raise ValueError(
                "Provide either 'complexity' OR individual values, not both."
            )

        if complexity:
            if complexity == "low":
                num_upper, num_digits, num_special = 1, 1, 0
            elif complexity == "medium":
                num_upper, num_digits, num_special = 2, 2, 1
            elif complexity == "high":
                num_upper, num_digits, num_special = 3, 3, 2
            else:
                raise ValueError(f"Unknown complexity level: {complexity}")

        # Default fallback
        if num_upper is None and num_digits is None and num_special is None:
            pool = string.ascii_letters + string.digits + string.punctuation
            return "".join(self._rng.choices(list(pool), k=length))

        # Normalize unset values
        num_upper = num_upper or 0
        num_digits = num_digits or 0
        num_special = num_special or 0

        if num_upper + num_digits + num_special > length:
            raise ValueError("Sum of complexity constraints exceeds total length.")

        chars: list[str] = []
        chars += [self._rng.choice(string.ascii_uppercase) for _ in range(num_upper)]
        chars += [self._rng.choice(string.digits) for _ in range(num_digits)]
        chars += [self._rng.choice(special_chars) for _ in range(num_special)]
        chars += [
            self._rng.choice(string.ascii_lowercase) for _ in range(length - len(chars))
        ]

        self._rng.shuffle(chars)
        return "".join(chars)

    def generate_token(self, length: int = 32, charset: Optional[str] = None) -> str:
        chars = charset or (string.ascii_letters + string.digits)
        return "".join(self._rng.choices(chars, k=length))

    def generate_uuid(self) -> str:
        return str(uuid.uuid4())

    def _generate_name(self):
        self.last_first_name = self._rng.choice(self.first_names)
        self.last_last_name = self._rng.choice(self.last_names)

    def load_names(self, first_names_path: str, last_names_path: str) -> None:
        self.first_names = [
            line.strip().lower() for line in open(first_names_path) if line.strip()
        ]
        self.last_names = [
            line.strip().lower() for line in open(last_names_path) if line.strip()
        ]

    def generate_name_dict(self) -> dict:
        """Generate and return a dict with first and last name."""
        self._generate_name()
        return {
            "first_name": self.last_first_name,
            "last_name": self.last_last_name,
        }

    def generate_core_identity(self, name: dict, spec: IdentitySpec) -> dict:
        """Generate username, email, password, created_at."""
        self.last_first_name = name["first_name"]
        self.last_last_name = name["last_name"]

        identity = {
            "first_name": self.last_first_name,
            "last_name": self.last_last_name,
            "username": self.generate_username(spec.username_format),
            "email": self.generate_email(spec.domain, spec.email_format),
            "password": self._providers["password"].generate(
                self._rng, spec.overrides.get("password", {})
            ),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        return identity

    def generate_extras(self, spec: IdentitySpec) -> dict:
        """Generate token, address, phone, etc."""
        extras = {}

        if spec.include_token:
            extras["token"] = self._providers["token"].generate(
                self._rng, spec.overrides.get("token", {})
            )

        for extra in spec.extras:
            if extra in self._providers:
                extras[extra] = self._providers[extra].generate(
                    self._rng, spec.overrides.get(extra, {})
                )

        return extras

    def generate_identity(self, spec: Optional[IdentitySpec] = None, **kwargs) -> dict:
        if spec is None:
            spec = IdentitySpec(**kwargs)

        name = self.generate_name_dict()
        core = self.generate_core_identity(name, spec)
        extras = self.generate_extras(spec)

        identity = {**core, **extras}
        self.last_identity = identity
        return identity

    def generate_from_spec(self, spec: IdentitySpec) -> dict:
        return self._generate_with_spec(spec)

    def save_identity(self, filepath: str) -> None:
        if not hasattr(self, "last_identity"):
            raise ValueError("No identity generated yet.")
        with open(filepath, "w") as f:
            json.dump(self.last_identity, f, indent=2)

    def load_identity(self, filepath: str) -> dict:
        with open(filepath, "r") as f:
            self.last_identity = json.load(f)

        self.last_first_name = self.last_identity["first_name"]
        self.last_last_name = self.last_identity["last_name"]
        return self.last_identity

    def as_dict(self) -> dict:
        if not hasattr(self, "last_identity"):
            raise ValueError("No identity generated yet.")
        return self.last_identity

    def as_json(self, indent: int = 2) -> str:
        return json.dumps(self.as_dict(), indent=indent)
