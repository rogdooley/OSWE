AsyncIO Usage Patterns in PoC Scripts

1. When to Use asyncio
	•	Need high concurrency (e.g., token spraying, brute force, directory scanning)
	•	Using httpx.AsyncClient
	•	Calling any async-based libraries (databases, I/O, etc.)

2. Minimal Async Usage

If only a single function (e.g., token brute force) requires asyncio, keep the rest of the script synchronous:

import asyncio
import httpx

def sync_part(session_cookie):
    print(f"Using session: {session_cookie}")

async def get_valid_session() -> httpx.Cookies:
    async with httpx.AsyncClient() as client:
        # Token spray or brute force logic
        return client.cookies

async def main():
    session = await get_valid_session()
    sync_part(session)

if __name__ == "__main__":
    asyncio.run(main())

Comment Example:

# NOTE:
# - async used here only to obtain session via brute force
# - rest of PoC is synchronous, but asyncio still required

3. Reminder Template for Scripts

# === REMINDER ===
# Async usage required for:
#   - httpx.AsyncClient
#   - large concurrent scans (asyncio.gather / semaphores)
#   - async-compatible I/O (files, DB, etc.)
#
# If only one section requires async (e.g., session brute force),
# keep it isolated and switch back to sync as needed.
# =================

4. Avoiding AsyncIO When Not Needed

If PoC has no async functions:

def main():
    # This is a sync PoC for now.
    ...

if __name__ == "__main__":
    main()


5. Decorator Utility (LLM recommended...needs some research and testing)

Allow toggling between sync and async HTTP clients depending on context:

import functools

def async_only_if_needed(is_async):
    def decorator(func):
        if is_async:
            return func
        else:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                raise RuntimeError("This function is async-only in current context.")
            return wrapper
    return decorator

# Usage
@async_only_if_needed(is_async=True)
async def run_bruteforce():
    ...



