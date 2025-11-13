import argparse
import requests
import time

from concurrent.futures import ThreadPoolExecutor, as_completed

"""
Submit fetch_url tasks to the thread pool.

Each call to executor.submit schedules fetch_url to run in a separate thread.
We pass the URL and timeout to each task. The result of submit() is a Future object,
which represents the pending result of that call.

We store each Future as a key in a dictionary, with the original URL as the value,
so we can later match results back to the URLs that triggered them.

Process completed tasks as they finish.

Using concurrent.futures.as_completed, we get each Future as soon as its thread finishes.
Calling .result() retrieves the return value of fetch_url for that Future.

If the task completed with an error, fetch_url returns an error string in the result tuple,
which we check and display accordingly. This lets us handle slow or failing URLs gracefully,
and show output as soon as each task completes.
"""

def fetch_url(url, timeout=5):
    try:
        response = requests.get(url, timeout=timeout)
        return (url, response.status_code, len(response.content), None)
    except Exception as e:
        return (url, "ERROR", None, f"{e}")


def parse_args():
    parser = argparse.ArgumentParser(description="Description of your script.")
    
    parser.add_argument("--workers", type=int, required=False, help="Set the maximum number of threads")
    parser.add_argument('--url-file', type=str, required=False, help="Load URLs from a file")
    parser.add_argument('--timeout', type=float, required=False, help="Request timeout")
    
    return parser.parse_args()


def main():

    args = parse_args()
    max_workers = [2, 5, 10 , 20]

    if args.url_file:
        URLS = [line.strip() for line in open(args.url_file)]
    else:
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


    if args.workers:
        start = time.perf_counter()
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            future_to_url = {executor.submit(fetch_url, url, args.timeout or 5): url for url in URLS}
            
            for future in as_completed(future_to_url):
                url, status, size, error = future.result()
                if error:
                    print(f"{url} -> Status: {status}, Error: {error}")
                else:
                    print(f"{url} -> Status: {status}, Size: {size} bytes")
        end = time.perf_counter()
        elapsed_time = end - start
        print(f"Execution time using {args.workers} threads: {elapsed_time:.6f} seconds")
    else:
        for worker in max_workers:
            start = time.perf_counter()
            with ThreadPoolExecutor(max_workers=worker) as executor:
                future_to_url = {executor.submit(fetch_url, url, args.timeout or 5): url for url in URLS}
                for future in as_completed(future_to_url):
                    url, status, size, error = future.result()
                    if error:
                        print(f"{url} -> Status: {status}, Error: {error}")
                    else:
                        print(f"{url} -> Status: {status}, Size: {size} bytes")
            end = time.perf_counter()
            elapsed_time = end - start
            print(f"Execution time using {worker} threads: {elapsed_time:.6f} seconds")



if __name__ == "__main__":
    main()