import argparse
import requests
import sys
import json
import shutil
import subprocess
import time

from bs4 import BeautifulSoup
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import Optional, Literal, Callable
from concurrent.futures import ThreadPoolExecutor

root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

# If commomn isn't in ../../common, change root dir or change the imports as appropriate
from common.offsec_logger import OffsecLogger
from common.file_transfer_server import FileTransferServer
from common.data_faker import DataFaker

logger = OffsecLogger(logfile="erka.log", debug=True)
ARTIFACT_DIR = Path("artifacts")


@dataclass
class ExploitContext:
    target_ip: str
    target_port: str
    attacker_ip: str
    attacker_port: str
    protocol: str = "http"

    # Auth state
    token: Optional[str] = None
    token_name: Optional[str] = None
    session_cookie: Optional[str] = None

    # Metadata
    vuln_name: Optional[str] = None
    poc_id: Optional[str] = None
    notes: str = ""

    # Runtime fields (ignored in serialization)
    output_path: Path = field(
        default_factory=lambda: Path("exploit_context.json"), repr=False
    )

    def __post_init__(self):
        if isinstance(self.output_path, str):
            self.output_path = Path(self.output_path)

    def target_url(self) -> str:
        return f"{self.protocol}://{self.target_ip}:{self.target_port}"

    def attacker_url(self) -> str:
        return f"{self.protocol}://{self.attacker_ip}:{self.attacker_port}"

    def save(self) -> None:
        """Persist context to a JSON file (excluding runtime fields)."""
        serializable_dict = {
            k: str(v) if isinstance(v, Path) else v
            for k, v in asdict(self).items()
            if k != "output_path"
        }
        with self.output_path.open("w") as f:
            json.dump(serializable_dict, f, indent=2)

    def load(self) -> None:
        """Restore fields from saved file if exists."""
        if self.output_path.exists():
            with self.output_path.open() as f:
                data = json.load(f)
            for key, value in data.items():
                if key == "output_path":
                    setattr(self, key, Path(value))
                else:
                    setattr(self, key, value)


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


def spawn_external_listener(listening_port: int):
    cmd = f"bash -c 'nc -lvnp {listening_port}; echo Press enter to close; read'"
    if shutil.which("gnome-terminal"):
        subprocess.Popen(["gnome-terminal", "--", "bash", "-c", cmd])
    elif shutil.which("x-terminal-emulator"):
        subprocess.Popen(["x-terminal-emulator", "-e", cmd])
    else:
        print(f"[!] No terminal available. Run manually:\n{cmd}")


def parse_args():
    parser = argparse.ArgumentParser(description="OSWE Chat Application Exploit.")

    parser.add_argument("--target-ip", type=str, required=True, help="Input file path")
    parser.add_argument("--target-port", type=int, default=80, help="Input file path")
    parser.add_argument(
        "--password",
        nargs="?",
        const=None,
        help="Password for username. If left blank, a random password will be generated.",
    )
    parser.add_argument(
        "--password-length",
        type=int,
        default=16,
        help="Length of the password if generated.",
    )
    parser.add_argument(
        "--listening-port",
        type=int,
        default=9001,
        help="Port to listen for reverse shell (default: 9001)",
    )
    parser.add_argument(
        "--listening-ip", type=str, help="IP to listen on for reverse shell"
    )
    parser.add_argument(
        "--delay",
        type=int,
        default=3,
        help="Response delay in seconds for timing inference",
    )
    parser.add_argument(
        "--user-file", type=str, default="user.json", help="Existing exploit user"
    )
    parser.add_argument(
        "--register",
        type=str2bool,
        default=False,
        help="Has the user already been registered.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    Path(ARTIFACT_DIR).mkdir(parents=True, exist_ok=True)

    proxies = {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"}

    ctx = ExploitContext(
        target_ip=args.target_ip,
        target_port=args.target_port,
        attacker_ip=args.listening_ip,
        attacker_port=args.listening_port,
        protocol="http",
        vuln_name="Erka",
        poc_id="01",
    )

    if not (args.target_ip or args.target_port):
        ctx.load()

    user = DataFaker()

    if args.register or not Path(args.user_file).exists():
        logger.info("Generating user...")
        identity = user.generate_identity(
            domain="evil.io",
            username_format="{f}_{last}{##}",
            email_format="{first}.{last}{##}",
            password_length=16,
            num_upper=2,
            num_digits=2,
            num_special=1,
            include_uuid=False,
            include_token=False,
        )
        user.save_identity(args.user_file)
        logger.success(f"User generated: {identity}")
    else:
        identity = user.load_identity(args.user_file)
        user.last_identity = identity
        logger.info(f"Loaded user from file : {identity}")

    # Add code

    ctx.save()


if __name__ == "__main__":
    main()
