import argparse
import os
import socket
import threading
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

"""
serve_once.py

Author: Roger Dooley
Purpose: Serve a single file one time via HTTP and shut down automatically after serving.

This script is designed for stealthy file delivery or payload drops in exploit chains,
red team operations, or controlled environments like OSWE labs.

Usage:
    python3 serve_once.py payload.zip

Features:
- Randomized route support
- One-time delivery (closes server after single request)
- Logs connection source and file served

Requires: flask

(c) Roger Dooley
Reusable Scripts for Security Labs and PoCs

This script is free to use, modify, and share for educational and lawful security testing purposes only.
Attribution required if redistributed.
"""


class SingleUseHandler(SimpleHTTPRequestHandler):
    file_requested = False
    file_name = None

    def do_GET(self):
        if self.path.lstrip("/") == self.file_name:
            SingleUseHandler.file_requested = True
        return super().do_GET()


def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        return sock.connect_ex(("localhost", port)) == 0


def wait_for_port(port: int, wait_secs: int):
    while is_port_in_use(port):
        print(f"[!] Port {port} is in use. Waiting {wait_secs} seconds...")
        time.sleep(wait_secs)


def start_server(file_path: Path, port: int):
    os.chdir(file_path.parent)
    SingleUseHandler.file_name = file_path.name
    httpd = HTTPServer(("0.0.0.0", port), SingleUseHandler)

    def serve():
        print(
            f"[+] Hosting {file_path.name} at http://localhost:{port}/{file_path.name}"
        )
        httpd.serve_forever()

    server_thread = threading.Thread(target=serve)
    server_thread.start()

    try:
        while not SingleUseHandler.file_requested:
            time.sleep(1)
    finally:
        print("[*] File served. Shutting down server...")
        httpd.shutdown()
        server_thread.join()


def file_path(value):
    p = Path(value)
    if not p.is_file():
        raise argparse.ArgumentTypeError(f"File '{value}' does not exist.")
    return p


def main():
    parser = argparse.ArgumentParser(
        description="Serve a file once via temporary HTTP server."
    )
    parser.add_argument("file", type=file_path, help="Path to the file to serve")
    parser.add_argument(
        "--port", type=int, default=8000, help="Port to host the server on"
    )
    parser.add_argument(
        "--wait",
        type=int,
        default=30,
        help="Time to wait between port availability checks (in seconds)",
    )
    args = parser.parse_args()

    if not args.file.exists():
        print(f"[!] Error: File '{args.file}' does not exist.")
        return

    wait_for_port(args.port, args.wait)
    start_server(args.file, args.port)


if __name__ == "__main__":
    main()
