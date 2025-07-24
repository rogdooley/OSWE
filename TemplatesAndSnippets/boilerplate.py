import argparse
import requests

from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

# If commomn isn't in ../../common, change root dir or change the imports as appropriate
from common.offsec_logger import OffsecLogger
from common.file_transfer_server import FileTransferServer


def parse_args():
    parser = argparse.ArgumentParser(description="OSWE Chat Application Exploit.")

    parser.add_argument("--target", type=str, required=True, help="Input file path")
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

    return parser.parse_args()


def main():
    args = parse_args()

    # ! TODO


if __name__ == "__main__":
    main()
