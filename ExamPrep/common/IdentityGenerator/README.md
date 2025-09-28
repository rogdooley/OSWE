# IdentityGenerator

`IdentityGenerator` is a flexible identity generation tool designed for red team operations, OSWE-style exploit development, CTF automation, and test data generation. It supports customizable formats, password/token generation, and optional address/phone fields.

## Features

- Configurable username/email formats (e.g. `f.lastname`, `first.last##`)
- Domain override support
- Password generation with complexity rules or custom counts
- Token generation with charset presets, min/max Unicode range, or custom sets
- UUID4 support
- Optional identity fields like:
  - Token
  - Address (street, city, state, zip)
  - Phone (US-style numbers)
- Save/load generated identities to/from JSON
- CLI usage and scripting support

## Installation

Clone the repository or copy the `IdentityGenerator/` folder into your project:


Or add the folder to your own project under a shared `common/` directory.

No external dependencies required.

## CLI Usage

```bash
python -m IdentityGenerator --json
```

### Options:

```bash
--domain EXAMPLE.COM             Override domain
--username-format FORMAT         Username format (e.g. f.lastname)
--email-format FORMAT            Email local format (e.g. first.last##)
--include-token                  Include a token in the identity
--extra address,phone            Include extra fields (comma-separated)
--override-file FILE.json        Load generation overrides from a JSON file
--json                           Print identity as JSON
--save FILE                      Save output to a JSON file
--seed INT                       Seed the random generator for reproducibility
```

### Example:

```bash
python -m IdentityGenerator \
  --domain hackme.local \
  --username-format f.lastname \
  --email-format first.last \
  --include-token \
  --extra address,phone \
  --json
```

## Programmatic Use

```python
from IdentityGenerator.identity_generator import IdentityGenerator
from IdentityGenerator.specs.identity_spec import IdentitySpec

gen = IdentityGenerator(seed=1234)

spec = IdentitySpec(
    domain="ctf.local",
    username_format="f.lastname",
    email_format="first.last##",
    include_token=True,
    extras=["address", "phone"],
    overrides={
        "password": {
            "length": 16,
            "num_upper": 2,
            "num_digits": 2,
            "num_special": 1
        },
        "token": {
            "preset": "base64url",
            "length": 24
        }
    }
)

identity = gen.generate_identity(spec)
print(identity)
```

## Output Format

The identity is returned as a dictionary (or JSON) with keys such as:

```json
{
  "first_name": "Alice",
  "last_name": "Nguyen",
  "username": "anguyen83",
  "email": "alice.nguyen83@example.com",
  "password": "tA3!mdkqlsmvzhfp",
  "token": "qL78UD_-uC2eRIQKPJnb0Iig",
  "created_at": "2025-08-13T23:55:00.000Z",
  "address": {
    "street": "312 Maple Avenue",
    "city": "Springfield",
    "state": "CA",
    "zip": "90210"
  },
  "phone": "(415) 872-1123"
}
```

## License

MIT License 

## Author

Roger Dooley
