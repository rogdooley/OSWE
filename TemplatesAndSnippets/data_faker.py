import random
import string
import uuid
import secrets
import json

from typing import Optional


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
    """

    def __init__(self, seed: Optional[int] = None):
        self.rng = random.Random(seed)
        self.first_names = [
            "Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", "Heidi",
            "Ivan", "Judy", "Karl", "Laura", "Mallory", "Nina", "Oscar", "Peggy",
            "Quinn", "Ruth", "Steve", "Trudy"
        ]
        self.last_names = [
            "Anderson", "Baker", "Clark", "Davis", "Evans", "Foster", "Garcia",
            "Harris", "Iverson", "Johnson", "Knight", "Lewis", "Miller", "Nguyen",
            "Owens", "Perry", "Quinn", "Roberts", "Stewart", "Turner"
        ]
        self.default_domains = [
            "example.com", "testmail.org", "fakemail.net", "mailinator.com",
            "inbox.test", "demo.site", "mockdomain.co", "tempmail.dev",
            "sandbox.io", "fakeinbox.xyz"
        ]


    def generate_username(self, format: str = "firstlast##") -> str:
        if not hasattr(self, 'last_first_name') or not hasattr(self, 'last_last_name'):
            self._generate_name()
        first, last = self.last_first_name.lower(), self.last_last_name.lower()
        number = str(self.rng.randint(10, 99))

        username = format
        username = username.replace("first", first)
        username = username.replace("last", last)
        username = username.replace("f", first[0])
        username = username.replace("##", number)

        return username


    def generate_email(self, domain: Optional[str] = None, format: str = "firstlast##") -> str:
        if not hasattr(self, 'last_first_name') or not hasattr(self, 'last_last_name'):
            self._generate_name()

        domain = domain or self.rng.choice(self.default_domains)
        first, last = self.last_first_name, self.last_last_name
        number = str(self.rng.randint(10, 99))

        email_local = format
        email_local = email_local.replace("first", first)
        email_local = email_local.replace("last", last)
        email_local = email_local.replace("f", first[0])
        email_local = email_local.replace("##", number)

        return f"{email_local}@{domain}"
        

    def generate_password(self, length: int = 12) -> str:
        chars = string.ascii_letters + string.digits + string.punctuation
        return ''.join(secrets.choice(chars) for _ in range(length))

    def generate_token(self, length: int = 32, charset: Optional[str] = None) -> str:
        chars = charset or (string.ascii_letters + string.digits)
        return ''.join(self.rng.choices(chars, k=length))

    def generate_uuid(self) -> str:
        return str(uuid.uuid4())

    def _generate_name(self):
        self.last_first_name = self.rng.choice(self.first_names)
        self.last_last_name = self.rng.choice(self.last_names)


    def load_names(self, first_names_path: str, last_names_path: str) -> None:
        self.first_names = [line.strip().lower() for line in open(first_names_path) if line.strip()]
        self.last_names = [line.strip().lower() for line in open(last_names_path) if line.strip()]

    
    def generate_identity(self, domain: Optional[str] = None,
                      username_format: str = "firstlast##",
                      email_format: str = "firstlast##",
                      password_length: int = 12) -> dict:
        self._generate_name()

        identity = {
            "first_name": self.last_first_name,
            "last_name": self.last_last_name,
            "username": self.generate_username(username_format),
            "email": self.generate_email(domain, email_format),
            "password": self.generate_password(password_length),
            "uuid": self.generate_uuid(),
            "token" : self.generate_token()
        }

        self.last_identity = identity
        return identity

    
    def save_identity(self, filepath: str) -> None:
        if not hasattr(self, 'last_identity'):
            raise ValueError("No identity generated yet.")
        with open(filepath, 'w') as f:
            json.dump(self.last_identity, f, indent=2)