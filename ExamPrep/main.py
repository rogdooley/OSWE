import argparse
import httpx
import asyncio
import aiofiles
import sys
import json
import shutil
import subprocess
import time
import base64
import secrets
import re
import uuid
import urllib.parse


from bs4 import BeautifulSoup
from pathlib import Path
from dataclasses import dataclass, asdict, field, fields
from typing import Optional, Literal, Callable, Any, Type

root_dir = Path(__file__).resolve().parent.parent
# sys.path.append(str(root_dir)) # failed to work in exam setup
sys.path.insert(0, str(root_dir))


# If common isn't in ../../common, change root dir or change the imports as appropriate
from common.offsec_logger import OffsecLogger
from common.file_transfer_server import FileTransferServer
from common.IdentityGenerator.identity_generator import IdentityGenerator
from common.IdentityGenerator.specs.identity_spec import IdentitySpec


ARTIFACT_DIR = Path("artifacts")
Identity = dict[str, Any]


CHARSETS = {
    "alpha": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "alnum": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
    "hex": "0123456789abcdef",
    "ascii": "".join(chr(i) for i in range(32, 127)),  # printable ASCII
    "symbols": "!@#$%^&*()-_=+[{]}\\|;:'\",<.>/?`~",
    "base64": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+/=",
    "numeric": "0123456789",
}


@dataclass(slots=True)
class ExploitContext:
    target_ip: str
    web_port: int
    api_port: int
    attacker_ip: str
    attacker_port: int
    protocol: str = "http"

    # Auth state
    token: Optional[str] = None
    token_name: Optional[str] = None
    session_cookie: Optional[str] = None

    # Metadata
    vuln_name: Optional[str] = None
    poc_id: Optional[str] = None
    notes: str = ""

    # Runtime-only fields
    output_path: Path = field(
        default_factory=lambda: Path("exploit_context.json"), repr=False
    )

    # --- Factory constructor from argparse ---

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> "ExploitContext":
        """Build an ExploitContext from CLI arguments."""
        return cls(
            target_ip=args.target_ip,
            web_port=args.target_port,  # maps to --target-port
            api_port=args.target_api_port,  # maps to --target-api-port
            attacker_ip=args.listening_ip,  # maps to --listening-ip
            attacker_port=args.listening_port,  # maps to --listening-port
        )

    # --- URL helpers ---

    def _make_url(self, host: str, port: int) -> str:
        """Return protocol://host[:port], omitting default ports."""
        default_port = 80 if self.protocol == "http" else 443
        port_part = f":{port}" if port != default_port else ""
        return f"{self.protocol}://{host}{port_part}"

    def web_url(self) -> str:
        return self._make_url(self.target_ip, self.web_port)

    def api_url(self) -> str:
        return self._make_url(self.target_ip, self.api_port)

    def attacker_url(self) -> str:
        return self._make_url(self.attacker_ip, self.attacker_port)

    # --- Persistence ---

    def save(self) -> None:
        """Persist context to a JSON file (excluding runtime-only fields)."""
        serializable_dict = {
            k: str(v) if isinstance(v, Path) else v
            for k, v in asdict(self).items()
            if k != "output_path"
        }
        with self.output_path.open("w") as f:
            json.dump(serializable_dict, f, indent=2)

    @classmethod
    def from_file(cls, path: Path) -> "ExploitContext":
        """Create a new context from a saved file, ignoring unknown fields."""
        with path.open() as f:
            data = json.load(f)

        valid_keys = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in data.items() if k in valid_keys}

        # Cast ports back to int if JSON saved them as str
        for port_key in ("web_port", "api_port", "attacker_port"):
            if port_key in filtered_data and isinstance(filtered_data[port_key], str):
                filtered_data[port_key] = int(filtered_data[port_key])

        ctx = cls(**filtered_data)
        ctx.output_path = path
        return ctx


def str2bool(v: str) -> bool:
    return v.lower() in ("yes", "true", "1")


def spawn_external_listener(listening_port: int):
    cmd = f"bash -c 'nc -lvnp {listening_port}; echo Press enter to close; read'"
    if shutil.which("gnome-terminal"):
        subprocess.Popen(["gnome-terminal", "--", "bash", "-c", cmd])
    elif shutil.which("x-terminal-emulator"):
        subprocess.Popen(["x-terminal-emulator", "-e", cmd])
    else:
        print(f"[!] No terminal available. Run manually:\n{cmd}")


def check_response(
    response: httpx.Response,
    logger,
    action: str,
    exc_type: Type[Exception] = ValueError,
) -> None:
    """
    Validate response status == 200. Otherwise log and raise.

    Parameters:
        response: httpx.Response
        logger: OffsecLogger
        action: str - description of the action, e.g. "register user"
        exc_type: Exception class to raise on failure
    """
    if response.status_code != 200:
        logger.error(f"Unable to {action}: {response.text}")
        raise exc_type(f"{action.capitalize()} failed: {response.status_code}")


def parse_args():
    parser = argparse.ArgumentParser(description="OSWE Application Exploit.")

    # --- Target options ---
    target_group = parser.add_argument_group("Target options")
    target_group.add_argument(
        "--target-ip", type=str, required=True, help="Target server IP address"
    )
    target_group.add_argument(
        "--target-port",
        type=int,
        default=80,
        help="Target web frontend port (default: 80)",
    )
    target_group.add_argument(
        "--target-api-port",
        type=int,
        default=5000,
        help="Target API port (default: 5000)",
    )

    # --- Attacker options ---
    attacker_group = parser.add_argument_group("Attacker options")
    attacker_group.add_argument(
        "--listening-ip",
        type=str,
        default="127.0.0.1",
        help="IP to listen on for reverse shell (default: 127.0.0.1)",
    )
    attacker_group.add_argument(
        "--listening-port",
        type=int,
        default=9001,
        help="Port to listen for reverse shell (default: 9001)",
    )

    # --- Exploit options ---
    exploit_group = parser.add_argument_group("Exploit options")
    exploit_group.add_argument(
        "--delay",
        type=int,
        default=3,
        help="Response delay in seconds for timing inference (default: 3)",
    )

    # --- Identity options ---
    identity_group = parser.add_argument_group("Identity options")
    identity_group.add_argument(
        "--user-file",
        type=str,
        default="user.json",
        help="Path to existing exploit user JSON (default: user.json)",
    )
    identity_group.add_argument(
        "--save-identity",
        type=str,
        help="Path to save newly generated identity JSON",
    )
    identity_group.add_argument(
        "--register",
        action="store_true",
        default=False,
        help="Whether the user has already been registered",
    )
    identity_group.add_argument(
        "--complexity", choices=["low", "medium", "high"], help="Password complexity"
    )
    identity_group.add_argument(
        "--include-address", action="store_true", help="Include street address"
    )
    identity_group.add_argument(
        "--include-phone", action="store_true", help="Include phone number"
    )

    optional_group = parser.add_argument_group("Optional options")
    optional_group.add_argument(
        "--charset",
        choices=CHARSETS.keys(),
        default="alnum",
        help="Charset to use for blind SQLi password extraction.",
    )
    optional_group.add_argument(
        "--proxy", default=None, help="Turn on Burp Suite proxy for debugging."
    )

    return parser.parse_args()


def main():
    args = parse_args()
    Path(ARTIFACT_DIR).mkdir(parents=True, exist_ok=True)

    if args.proxy:
        proxies = {"http://": args.proxy, "https://": args.proxy}
    else:
        proxies = None

    charset = CHARSETS[args.charset]

    log_name = Path.cwd().name
    logfile_path = ARTIFACT_DIR / f"{log_name}.log"
    logger = OffsecLogger(logfile=logfile_path, debug=True)

    ctx = ExploitContext.from_args(args)

    extras = []
    if args.include_address:
        extras.append("address")
    if args.include_phone:
        extras.append("phone")

    overrides = {}
    if args.complexity:
        overrides["password"] = {"complexity": args.complexity}

    spec = IdentitySpec(
        extras=extras,
        overrides=overrides,
    )

    generator = IdentityGenerator()
    identity = generator.generate_identity(spec)

    if args.save_identity:
        identity_path = ARTIFACT_DIR / args.save_identity
        generator.save_identity(identity_path)
        logger.info(f"Identity saved to {identity_path}")
    else:
        print(generator.as_json())

    # Add code

    ctx.save()


if __name__ == "__main__":
    main()
