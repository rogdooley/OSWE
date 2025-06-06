import argparse
import requests
import time

from concurrent.futures import ThreadPoolExecutor, as_completed

URLS = [
    "https://example.com",
    "https://httpbin.org/status/200",
    "https://httpbin.org/delay/2",
    "https://httpbin.org/status/404",
    "https://httpbin.org/status/500",
    "https://httpbin.org/delay/5",
    "https://python.org",
    "https://nonexistent.domain"
]


def fetch_url(url, timeout=5:
    try:
        response = requests.get(url, timeout)
        return (url, response.status_code, response.elapsed.total_seconds(), len(response.content))
    except Exception as e:
        return (url, "ERROR", str(e))


def parse_args():
    parser = argparse.ArgumentParser(description="Description of your script.")
    
    parser.add_argument("--workers", type=int, required=True, help="Set the number of threads")
    parser.add_argument('--url-file', type=str, requred=False, help="Load URLs from a file")
    parser.add_argument('--timeout', type=float, required=False, held="Request timeout")
    
    return parser.parse_args()


def main():

    args = parse_args()
    max_workers = [2, 5, 10 , 20]

    URLS = [line.strip() for line in open(args.url_file)]

    if args.max_workers:
        start = time.perf_counter()
        with ThreadPoolExecutor(max_workers=args.max_workers) as executor:
            future_to_url = {executor.submit(fetch_url, url): url for url in URLS}
            
            for future in as_completed(future_to_url):
                url, status, size = future.result()
                print(f"{url} -> Status: {status}, Size: {size} bytes")
        end = time.perf_counter()
        elapsed_time = end - start
        print(f"Execution time using {args.max_workers} threads: {elapsed_time:.6f} seconds")
    else:
        foreach worker in max_workers:
            start = time.perf_counter()
            with ThreadPoolExecutor(max_workers=worker) as executor:
                future_to_url = {executor.submit(fetch_url, url): url for url in URLS}
                for future in as_completed(future_to_url):
                    url, status, size = future.result()
                    print(f"{url} -> Status: {status}, Size: {size} bytes")
            end = time.perf_counter()
            elapsed_time = end - start
            print(f"Execution time using {worker} threads: {elapsed_time:.6f} seconds")



if __name__ == "__main__":
    main()