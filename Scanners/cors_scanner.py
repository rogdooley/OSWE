import requests
import argparse
import json
from urllib.parse import urlparse
from datetime import datetime
from pathlib import Path

"""
(c) Roger Dooley
Reusable Scripts for Security Labs and PoCs

This script is free to use, modify, and share for educational and lawful security testing purposes only.
Attribution required if redistributed.
"""

# Common origins used for testing
TEST_ORIGINS = [
    "https://evil.com",
    "null",
    "https://target.com.evil.com",
    "https://sub.target.com.evil.com",
    "file://",
    "http://localhost",
    "http://127.0.0.1",
    "https://127.0.0.1",
]

# Custom headers to test in preflight requests
CUSTOM_HEADERS = [
    "X-Test-Header",
    "Authorization",
    "Content-Type",
    "X-Requested-With",
    "X-Admin"
]

def analyze_response(r, origin, requested_header=None):
    headers = r.headers
    acao = headers.get("Access-Control-Allow-Origin", "")
    acac = headers.get("Access-Control-Allow-Credentials", "")
    acam = headers.get("Access-Control-Allow-Methods", "")
    acah = headers.get("Access-Control-Allow-Headers", "")
    misconfig = False

    # Misconfiguration checks
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
        "requested_header": requested_header,
        "status_code": r.status_code,
        "acao": acao,
        "acac": acac,
        "acam": acam,
        "acah": acah,
        "vulnerable": misconfig,
        "reason": reason,
        "headers": dict(headers)
    }

def scan_target(url, origins, custom_headers):
    results = {
        "target": url,
        "timestamp": datetime.utcnow().isoformat(),
        "origin_tests": [],
        "preflight_tests": [],
    }

    for origin in origins:
        # GET request test
        try:
            r = requests.get(url, headers={"Origin": origin}, timeout=10)
            result = analyze_response(r, origin)
            results["origin_tests"].append(result)
        except Exception as e:
            results["origin_tests"].append({
                "origin_tested": origin,
                "error": str(e)
            })

        # Preflight OPTIONS request with custom headers
        for ch in custom_headers:
            try:
                r2 = requests.options(url, headers={
                    "Origin": origin,
                    "Access-Control-Request-Method": "POST",
                    "Access-Control-Request-Headers": ch
                }, timeout=10)
                result2 = analyze_response(r2, origin, requested_header=ch)
                results["preflight_tests"].append(result2)
            except Exception as e:
                results["preflight_tests"].append({
                    "origin_tested": origin,
                    "requested_header": ch,
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

def print_summary(results):
    print("\n[+] Summary of Origin Tests:")
    for entry in results["origin_tests"]:
        if "error" in entry:
            print(f"  - {entry['origin_tested']}: ERROR — {entry['error']}")
        else:
            status = "VULNERABLE" if entry["vulnerable"] else "OK"
            print(f"  - {entry['origin_tested']}: {status} — {entry['reason']}")

    print("\n[+] Summary of Preflight Tests:")
    for entry in results["preflight_tests"]:
        if "error" in entry:
            print(f"  - {entry['origin_tested']} ({entry.get('requested_header', '-')}) → ERROR — {entry['error']}")
        else:
            status = "VULNERABLE" if entry["vulnerable"] else "OK"
            print(f"  - {entry['origin_tested']} ({entry.get('requested_header', '-')}) → {status} — {entry['reason']}")

def main():
    parser = argparse.ArgumentParser(description="CORS Misconfiguration Scanner")
    parser.add_argument("-u", "--url", help="Target URL to scan", required=True)
    parser.add_argument("-o", "--output", help="Output directory for logs", default="cors_logs")
    parser.add_argument("-x", "--extra-origins", help="Comma-separated extra origins to test")
    args = parser.parse_args()

    test_origins = TEST_ORIGINS.copy()
    if args.extra_origins:
        test_origins += [x.strip() for x in args.extra_origins.split(",")]

    print(f"[+] Scanning: {args.url}")
    results = scan_target(args.url, test_origins, CUSTOM_HEADERS)
    save_json_log(results, args.output)
    print_summary(results)

if __name__ == "__main__":
    main()
