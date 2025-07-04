from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Iterable

def run_threaded(
    func: Callable,
    items: Iterable,
    max_workers: int = 10,
    show_progress: bool = False
) -> list:
    """
    Executes `func(item)` over all items using a thread pool.
    Returns a list of results (None results are preserved).
    """
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_item = {executor.submit(func, item): item for item in items}
        for future in as_completed(future_to_item):
            item = future_to_item[future]
            try:
                result = future.result()
                results.append(result)
                if show_progress:
                    print(f"\r[*] Processed item: {item}", end='', flush=True)
            except Exception as e:
                print(f"\n[!] Exception on {item}: {e}")
    return results