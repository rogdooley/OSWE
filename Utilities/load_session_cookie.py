#!/usr/bin/env python3

import argparse
import json
from pathlib import Path

import requests


def load_session_cookie(session: requests.Session, path: Path):
    cookies = json.loads(path.read_text())
    for c in cookies:
        session.cookies.set(c["name"], c["value"], domain=c["domain"], path=c["path"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("infile", type=Path, help="Path to saved cookie JSON")
    parser.add_argument("url", help="URL to test authenticated access")
    args = parser.parse_args()

    s = requests.Session()
    load_session_cookie(s, args.infile)
    r = s.get(args.url)
    print(f"[+] Response from {args.url} - Status: {r.status_code}")
    print(r.text[:500])
