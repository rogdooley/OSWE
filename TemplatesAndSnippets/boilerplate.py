import argparse
import requests
import sys
import json
import shutil
import subprocess

from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import Optional

root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

# If commomn isn't in ../../common, change root dir or change the imports as appropriate
from common.offsec_logger import OffsecLogger
from common.file_transfer_server import FileTransferServer
from common.data_faker import DataFaker


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
    output_path: Path = field(default=Path("exploit_context.json"), repr=False)

    def target_url(self) -> str:
        return f"{self.protocol}://{self.target_ip}:{self.target_port}"

    def attacker_url(self) -> str:
        return f"{self.protocol}://{self.attacker_ip}:{self.attacker_port}"

    def save(self) -> None:
        """Persist context to a JSON file (excluding runtime fields)."""
        with self.output_path.open("w") as f:
            json.dump(asdict(self), f, indent=2)

    def load(self) -> None:
        """Restore fields from saved file if exists."""
        if self.output_path.exists():
            with self.output_path.open() as f:
                data = json.load(f)
            for key, value in data.items():
                setattr(self, key, value)


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
        "--user-file", type=str, default="user.json", help="Existing exploit user"
    )
    parser.add_argument(
        "--register",
        type=bool,
        default=False,
        help="Has the user already been registered.",
    )
    return parser.parse_args()


# Example request possibilties
def get(self, path: str, **kwargs) -> requests.Response:
    return requests.get(f"{self.target_url()}/{path.lstrip('/')}", **kwargs)


def post(self, path: str, data=None, json=None, **kwargs) -> requests.Response:
    return requests.post(
        f"{self.target_url()}/{path.lstrip('/')}", data=data, json=json, **kwargs
    )


def main():
    args = parse_args()

    ctx = ExploitContext(
        target_ip=args.target_ip,
        target_port=args.target_port,
        attacker_ip=args.listening_ip,
        attacker_port=args.listening_port,
        protocol="http",
        vuln_name="<INSERT>",
        poc_id="<INSERT>",
    )
    ctx.load()

    # Add code here

    ctx.save()


if __name__ == "__main__":
    main()
