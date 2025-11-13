import requests
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

URLS = [
    "https://example.com",
    "https://httpbin.org/get",
    "https://www.python.org",
    "https://www.wikipedia.org",
    "https://github.com"
]

def fetch_url(url):
    try:
        response = requests.get(url, timeout=5)
        return (url, response.status_code, len(response.content))
    except Exception as e:
        return (url, "ERROR", str(e))

def parse_args():
    parser = argparse.ArgumentParser(description="Description of your script.")
    
    parser.add_argument("--max-workers", type=int, required=True, help="Target")
    
    return parser.parse_args()


def main():

    args = parse_args()


    with ThreadPoolExecutor(max_workers=args.max_workers) as executor:
        future_to_url = {executor.submit(fetch_url, url): url for url in URLS}
        
        for future in as_completed(future_to_url):
            url, status, size = future.result()
            print(f"{url} -> Status: {status}, Size: {size} bytes")


if __name__ == "__main__":
    main()