#!/usr/bin/env python3

import argparse, json, requests
from http.cookiejar import Cookie
from pathlib import Path

def save_session_cookie(session: requests.Session, path: Path):
    cookie_dicts = [
        {
            "name": c.name,
            "value": c.value,
            "domain": c.domain,
            "path": c.path,
            "secure": c.secure,
            "expires": c.expires
        }
        for c in session.cookies
    ]
    path.write_text(json.dumps(cookie_dicts, indent=2))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="URL to fetch and extract cookies from")
    parser.add_argument("outfile", type=Path, help="Output JSON path")
    args = parser.parse_args()

    s = requests.Session()
    s.get(args.url)
    save_session_cookie(s, args.outfile)
    print(f"[+] Cookies saved to {args.outfile}")