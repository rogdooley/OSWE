from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Optional

@dataclass
class UserResult:
    id: int
    username: str

# Simulated function that needs static + dynamic args
def test_user_id(uid: int, base_url: str) -> Optional[UserResult]:
    if uid % 10 == 0:
        return UserResult(id=uid, username=f"user{uid}")
    return None

def make_check_uid(base_url: str):
    def check_uid(uid: int) -> Optional[UserResult]:
        return test_user_id(uid, base_url)
    return check_uid

def threaded_search(base_url: str, max_uid: int, threads: int = 10) -> list[UserResult]:
    check_uid = make_check_uid(base_url)
    with ThreadPoolExecutor(max_workers=threads) as executor:
        results = list(executor.map(check_uid, range(1, max_uid + 1)))
    return [r for r in results if r is not None]

if __name__ == "__main__":
    users = threaded_search("https://example.com/user/{ID}", max_uid=100, threads=10)
    for user in users:
        print(f"[+] Found user: {user.id} -> {user.username}")