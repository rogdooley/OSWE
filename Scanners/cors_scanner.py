#!/usr/bin/env python3
import requests
import argparse
import json
import os
from urllib.parse import urlparse
from datetime import datetime
from pathlib import Path

# Common origins used for testing
TEST_ORIGINS = [
    "https://evil.com",
    "null",
    "https://target.com.evil.com",
    "file://",
    "http://localhost",
    "http://127.0.0.1",
    "https://127.0.0.1",
]

def analyze_response(r, origin):
    headers = r.headers
    acao = headers.get("Access-Control-Allow-Origin", "")
    acac = headers.get("Access-Control-Allow-Credentials", "")
    misconfig = False

    # Basic checks for common misconfigs
    if acao == "*" and acac.lower() == "true":
        misconfig = True
        reason = "Wildcard ACAO with credentials"
    elif origin == acao and acac.lower() == "true":
        misconfig = True
        reason = f"Reflected ACAO with credentials for origin: {origin}"
    elif acao == "null":
        misconfig = True
        reason = "Null origin allowed"
    else:
        reason = "None"

    return {
        "origin_tested": origin,
        "status_code": r.status_code,
        "acao": acao,
        "acac": acac,
        "vulnerable": misconfig,
        "reason": reason,
        "headers": dict(headers)
    }

def scan_target(url, origins):
    results = {
        "target": url,
        "timestamp": datetime.utcnow().isoformat(),
        "origin_tests": [],
        "preflight_tests": [],
    }

    for origin in origins:
        try:
            r = requests.get(url, headers={"Origin": origin}, timeout=10)
            result = analyze_response(r, origin)
            results["origin_tests"].append(result)
        except Exception as e:
            results["origin_tests"].append({
                "origin_tested": origin,
                "error": str(e)
            })

        # Preflight OPTIONS request
        try:
            r2 = requests.options(url, headers={
                "Origin": origin,
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "X-Test-Header"
            }, timeout=10)
            result2 = analyze_response(r2, origin)
            results["preflight_tests"].append(result2)
        except Exception as e:
            results["preflight_tests"].append({
                "origin_tested": origin,
                "error": str(e)
            })

    return results

def save_json_log(results, output_dir):
    parsed = urlparse(results["target"])
    host = parsed.netloc.replace(":", "_")
    safe_time = results["timestamp"].replace(":", "-")
    filename = f"{host}_{safe_time}.json"
    path = Path(output_dir) / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"[+] Log saved to: {path}")

def main():
    parser = argparse.ArgumentParser(description="CORS Misconfiguration Scanner")
    parser.add_argument("-u", "--url", help="Target URL to scan", required=True)
    parser.add_argument("-o", "--output", help="Output directory for logs", default="cors_logs")
    parser.add_argument("-x", "--extra-origins", help="Add comma-separated extra origins to test")
    args = parser.parse_args()

    test_origins = TEST_ORIGINS.copy()
    if args.extra_origins:
        test_origins += [x.strip() for x in args.extra_origins.split(",")]

    print(f"[+] Scanning: {args.url}")
    results = scan_target(args.url, test_origins)
    save_json_log(results, args.output)

if __name__ == "__main__":
    main()

