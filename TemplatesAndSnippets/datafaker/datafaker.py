import random
import string
import uuid
import json

from typing import Optional
from datetime import datetime, timezone


class DataFaker:
    """
    Utility class for generating test data for OSWE and CTF exploit development.

    Methods:
        - generate_username(): Returns a random username.
        - generate_email(domain): Returns a random email address.
        - generate_password(length): Returns a random password.
        - generate_token(length, charset): Returns a random string token.
        - generate_uuid(): Returns a random UUID4 string.

    Examples:
        >>> faker = DataFaker()
        >>> faker.generate_username()
        'joeray99'
        >>> faker.generate_email()
        'marcyhicks21@example.com'
        >>> faker.generate_email(domain="evilcorp.local")
        'gparker47@evilcorp.local'
        >>> faker.generate_password(length=16)
        'z!Q9fj2Xc$L71Tuv'
        >>> faker.generate_token(length=12)
        'XZ89Aj1sdLE0'
        >>> faker.generate_uuid()
        '550e8400-e29b-41d4-a716-446655440000'

    Sample Usage:
        faker = DataFaker()
        identity = faker.generate_identity(
            domain="test.io",
            username_format="f.lastname",
            email_format="first.last##",
            password_length=16,
            num_upper=2,
            num_digits=2,
            num_special=1,
            include_uuid=False,
            include_token=False
        )

        faker.save_identity("exploit_user.json")
        loaded = faker.load_identity("exploit_user.json")
        print(loaded)
    """

    def __init__(self, seed: Optional[int] = None):
        self._rng = random.Random(seed)
        self._providers = {
            "password": PasswordProvider(),
            "token": TokenProvider(),
            # future "address": AddressProviderUS(), "phone": PhoneProviderUS()
        }
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

    def generate_username(self, format: str = "{first}{last}{##}") -> str:
        if not hasattr(self, "last_first_name") or not hasattr(self, "last_last_name"):
            self._generate_name()
        first, last = self.last_first_name.lower(), self.last_last_name.lower()
        number = str(self.rng.randint(10, 99))
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
        number = str(self.rng.randint(10, 99))
        initial = first[0]
        domain = domain or self.rng.choice(self.default_domains)

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
        if spec.include_uuid:
            identity["uuid"] = str(uuid.uuid4())

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
            return "".join(self.rng.choices(list(pool), k=length))

        # Normalize unset values
        num_upper = num_upper or 0
        num_digits = num_digits or 0
        num_special = num_special or 0

        if num_upper + num_digits + num_special > length:
            raise ValueError("Sum of complexity constraints exceeds total length.")

        chars: list[str] = []
        chars += [self.rng.choice(string.ascii_uppercase) for _ in range(num_upper)]
        chars += [self.rng.choice(string.digits) for _ in range(num_digits)]
        chars += [self.rng.choice(special_chars) for _ in range(num_special)]
        chars += [
            self.rng.choice(string.ascii_lowercase) for _ in range(length - len(chars))
        ]

        self.rng.shuffle(chars)
        return "".join(chars)

    def generate_token(self, length: int = 32, charset: Optional[str] = None) -> str:
        chars = charset or (string.ascii_letters + string.digits)
        return "".join(self.rng.choices(chars, k=length))

    def generate_uuid(self) -> str:
        return str(uuid.uuid4())

    def _generate_name(self):
        self.last_first_name = self.rng.choice(self.first_names)
        self.last_last_name = self.rng.choice(self.last_names)

    def load_names(self, first_names_path: str, last_names_path: str) -> None:
        self.first_names = [
            line.strip().lower() for line in open(first_names_path) if line.strip()
        ]
        self.last_names = [
            line.strip().lower() for line in open(last_names_path) if line.strip()
        ]

    def generate_address(self) -> str:
        streets = ["Main St", "Oak Ave", "Pine Rd", "Maple Dr", "Cedar Ln"]
        house_number = self.rng.randint(1, 9999)
        return f"{house_number} {self.rng.choice(streets)}"

    def generate_city(self) -> str:
        cities = ["Springfield", "Riverton", "Franklin", "Madison", "Clinton"]
        return self.rng.choice(cities)

    def generate_zip(self) -> str:
        return "".join(self.rng.choices(string.digits, k=5))

    def generate_phone(self) -> str:
        return f"{self.rng.randint(100, 999)}-{self.rng.randint(100, 999)}-{self.rng.randint(1000, 9999)}"

    def generate_identity(
        self,
        domain: Optional[str] = None,
        username_format: str = "{first}_{last}{##}",
        email_format: str = "{first}.{last}{##}",
        password_length: int = 12,
        num_upper: Optional[int] = None,
        num_digits: Optional[int] = None,
        num_special: Optional[int] = None,
        password_complexity: Optional[str] = None,
        include_uuid: bool = True,
        include_token: bool = True,
        include_address: bool = False,
        include_city: bool = False,
        include_zip: bool = False,
        include_phone: bool = False,
    ) -> dict:
        self._generate_name()
        identity = {
            "first_name": self.last_first_name,
            "last_name": self.last_last_name,
            "username": self.generate_username(username_format),
            "email": self.generate_email(domain, email_format),
            "password": self.generate_password(
                length=password_length,
                num_upper=num_upper,
                num_digits=num_digits,
                num_special=num_special,
                complexity=password_complexity,
            ),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        if include_uuid:
            identity["uuid"] = self.generate_uuid()
        if include_token:
            identity["token"] = self.generate_token()
        if include_address:
            identity["address"] = self.generate_address()
        if include_city:
            identity["city"] = self.generate_city()
        if include_zip:
            identity["zip"] = self.generate_zip()
        if include_phone:
            identity["phone"] = self.generate_phone()

        self.last_identity = identity
        return identity

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
