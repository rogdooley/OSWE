import asyncio
import httpx


async def try_token(
    token: str,
    url: str,
    client: httpx.AsyncClient,
    found_event: asyncio.Event,
    result: dict,
):
    if found_event.is_set():
        return
    try:
        resp = await client.post(url, json={"token": token})
        if resp.status_code == 200 and "session" in resp.text:
            print(f"[+] Valid token found: {token}")
            result["token"] = token
            result["session"] = resp.cookies.get("session")
            found_event.set()
    except Exception as e:
        pass


async def spray_tokens(url: str, tokens: list[str]) -> dict:
    found_event = asyncio.Event()
    result = {}

    async with httpx.AsyncClient(timeout=5) as client:
        tasks = [try_token(token, url, client, found_event, result) for token in tokens]
        await asyncio.gather(*tasks, return_exceptions=True)

    return result if found_event.is_set() else None


# Requires 3.11+
async def try_token_task_group(
    token: str,
    url: str,
    client: httpx.AsyncClient,
    found_event: asyncio.Event,
    result: dict,
):
    if found_event.is_set():
        return
    try:
        resp = await client.post(url, json={"token": token})
        if resp.status_code == 200 and "session" in resp.text:
            result["token"] = token
            result["session"] = resp.cookies.get("session")
            found_event.set()
            # Let the exception bubble up to cancel TaskGroup
            raise asyncio.CancelledError()  # forces group exit (can also raise custom Done)
    except asyncio.CancelledError:
        raise
    except Exception:
        pass


async def spray_tokens_task_group(url: str, tokens: list[str]) -> dict | None:
    result = {}
    found_event = asyncio.Event()
    async with httpx.AsyncClient(timeout=5) as client:
        try:
            async with asyncio.TaskGroup() as tg:
                for token in tokens:
                    tg.create_task(try_token(token, url, client, found_event, result))
        except* asyncio.CancelledError:
            # This is raised by TaskGroup once one task fails or raises CancelledError
            pass
    return result if found_event.is_set() else None


def chunked(seq: list[str], batch_size: int) -> list[list[str]]:
    for i in range(0, len(seq), batch_size):
        yield seq[i : i + batch_size]


async def spray_tokens_batched(
    url: str, tokens: list[str], batch_size: int = 100
) -> dict | None:
    found_event = asyncio.Event()
    result = {}

    async with httpx.AsyncClient(timeout=5) as client:
        for token_batch in chunked(tokens, batch_size):
            if found_event.is_set():
                break  # Stop if token already found

            try:
                async with asyncio.TaskGroup() as tg:
                    for token in token_batch:
                        tg.create_task(
                            try_token(token, url, client, found_event, result)
                        )
            except* asyncio.CancelledError:
                break  # Clean exit

    return result if found_event.is_set() else None
