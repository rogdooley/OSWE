#!/usr/bin/env python3
import argparse
import base64
import json
import socket
import threading
import time
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

"""
payload_listener.py

Author: Roger Dooley
Purpose: Simple HTTP listener to receive data exfiltration or payload callbacks.

This script prints all incoming POST requests to stdout and is useful for:
- Blind injection testing (e.g., XXE, SQLi, SSTI)
- Receiving exfiltrated content in PoCs
- Lightweight beacon listeners in labs

Usage:
    python3 payload_listener.py 8080

Features:
- Accepts and logs all POST body data
- Displays a banner on startup
- Runs until interrupted

Requires: flask

(c) Roger Dooley
Reusable Scripts for Security Labs and PoCs

This script is free to use, modify, and share for educational and lawful security testing purposes only.
Attribution required if redistributed.
"""

LOG_FILE = "received_payloads.log"

def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        return sock.connect_ex(("localhost", port)) == 0

def wait_for_port(port: int, wait_secs: int):
    warned = False
    while is_port_in_use(port):
        if not warned:
            print(f"[!] Port {port} is in use. Waiting for it to become free...")
            warned = True
        time.sleep(wait_secs)

def handle_payload(decoded: str, method: str):
    timestamp = datetime.utcnow().isoformat()
    entry = f"[{timestamp}] [{method}] {decoded}\n"
    print(entry.strip())
    with open(LOG_FILE, "a") as f:
        f.write(entry)

class PayloadHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, param_name="payload", decode_b64=True, allowed_method=None, **kwargs):
        self.param_name = param_name
        self.decode_b64 = decode_b64
        self.allowed_method = allowed_method
        super().__init__(*args, **kwargs)

    def _extract_payload(self, method):
        if method == "GET":
            qs = parse_qs(urlparse(self.path).query)
            return qs.get(self.param_name, [""])[0]
        elif method == "POST":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            content_type = self.headers.get("Content-Type", "")
            try:
                if "application/json" in content_type:
                    parsed = json.loads(body.decode())
                    return parsed.get(self.param_name, "")
                elif "application/x-www-form-urlencoded" in content_type:
                    parsed = parse_qs(body.decode())
                    return parsed.get(self.param_name, [""])[0]
                else:
                    return body.decode(errors="ignore")
            except Exception:
                return ""
        return ""

    def _respond(self, code, msg):
        self.send_response(code)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(msg.encode())

    def _process_request(self, method):
        raw = self._extract_payload(method)
        if not raw:
            self._respond(400, "Missing or invalid payload.")
            return
        try:
            data = base64.b64decode(raw).decode() if self.decode_b64 else raw
        except Exception as e:
            self._respond(400, f"Payload decode error: {e}")
            return
        handle_payload(data, method)
        self._respond(200, "Payload received.")

    def do_GET(self):
        if self.allowed_method and self.allowed_method != "GET":
            self._respond(405, "GET not allowed.")
        else:
            self._process_request("GET")

    def do_POST(self):
        if self.allowed_method and self.allowed_method != "POST":
            self._respond(405, "POST not allowed.")
        else:
            self._process_request("POST")

def run_server(port, param_name, decode_b64, allowed_method, wait_secs):
    def handler_factory(*args, **kwargs):
        return PayloadHandler(*args, param_name=param_name, decode_b64=decode_b64, allowed_method=allowed_method, **kwargs)

    wait_for_port(port, wait_secs)
    server = HTTPServer(("0.0.0.0", port), handler_factory)
    print(f"[+] Listening on http://0.0.0.0:{port}/ (waiting for payloads)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Server stopped.")

def main():
    parser = argparse.ArgumentParser(description="Host an HTTP server to receive base64 (or raw) payloads.")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on")
    parser.add_argument("--param", type=str, default="payload", help="Query/field name to extract")
    parser.add_argument("--b64", action="store_true", help="Decode the payload from base64")
    parser.add_argument("--method", choices=["GET", "POST"], help="Restrict to a single HTTP method")
    parser.add_argument("--wait", type=int, default=5, help="Seconds to wait between port availability checks")
    args = parser.parse_args()

    run_server(args.port, args.param, args.b64, args.method, args.wait)

if __name__ == "__main__":
    main()