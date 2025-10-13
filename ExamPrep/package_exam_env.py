#!/usr/bin/env python3
import os
import tarfile
import subprocess
import argparse
from pathlib import Path

"""
package_exam_env.py - Archive and sanitize your OSWE/mock exam environment

This script recursively tars up a project directory (e.g., `oswe-mock`) while **excluding**
common development artifacts such as:

- `__pycache__/`, `.venv/`, `.pytest_cache/`, `artifacts/` directories
- `.log`, `.md`, `.jpeg`, `.lock` files
- README.md, Notes.md
- Additional user-specified files or directories via `--exclude`

If `requirements.txt` does not exist at the root, it will be generated automatically using `pip freeze`.

It also checks for `pyproject.toml` or `requirements.txt` inside each `machine-*` subdirectory and issues a warning if they're missing.

The final `.tar.gz` archive will contain only essential code and files for submission or backup.

---
Usage:
    python3 package_exam_env.py --path oswe-mock --output oswe-mock.tar.gz

    # With custom excludes (e.g., ignore screenshots and `.idea`)
    python3 package_exam_env.py --path oswe-mock --exclude screenshots --exclude .idea

---
After creation, you can base64-encode the archive with:

    base64 oswe-mock.tar.gz > oswe-mock.b64

"""

DEFAULT_EXCLUDE_DIRS = {
    ".venv",
    "__pycache__",
    ".pytest_cache",
    "artifacts",
}
DEFAULT_EXCLUDE_EXTS = {".log", ".md", ".jpeg", ".lock"}
DEFAULT_EXCLUDE_FILES = {"README.md", "Notes.md"}


def should_exclude(path: Path, user_excludes: set[str]) -> bool:
    parts = set(path.parts)
    if parts & (DEFAULT_EXCLUDE_DIRS | user_excludes):
        return True
    if path.name in DEFAULT_EXCLUDE_FILES:
        return True
    if path.suffix in DEFAULT_EXCLUDE_EXTS:
        return True
    return False


def generate_requirements_if_missing(root: Path):
    req_file = root / "requirements.txt"
    if req_file.exists():
        print("[+] requirements.txt already exists.")
        return
    print("[*] requirements.txt not found, generating with 'pip freeze'...")
    try:
        result = subprocess.run(
            ["pip", "freeze"], check=True, text=True, capture_output=True
        )
        req_file.write_text(result.stdout)
        print("[+] requirements.txt created.")
    except subprocess.CalledProcessError as e:
        print("[-] Failed to generate requirements.txt:", e)


def warn_if_missing_pyproject_or_reqs(root: Path):
    for subdir in root.iterdir():
        if subdir.is_dir() and subdir.name.startswith("machine-"):
            if not any(
                (subdir / fname).exists()
                for fname in ("pyproject.toml", "requirements.txt")
            ):
                print(f"[!] Warning: No pyproject.toml or requirements.txt in {subdir}")


def tar_project(root: Path, output_file: Path, user_excludes: set[str]):
    print(f"[*] Creating archive: {output_file}")
    with tarfile.open(output_file, "w:gz") as tar:
        for path in root.rglob("*"):
            if output_file in path.parents or path == output_file:
                continue
            if should_exclude(path.relative_to(root), user_excludes):
                continue
            tar.add(path, arcname=path.relative_to(root))
    print("[+] Archive created.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=str, default=".", help="Root project directory")
    parser.add_argument(
        "--output", type=str, default="exam_env.tar.gz", help="Output tar.gz filename"
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="Additional directories to exclude",
    )

    args = parser.parse_args()
    root = Path(args.path).resolve()
    output = Path(args.output).resolve()
    user_excludes = set(args.exclude)

    if not root.exists():
        print(f"[-] Path not found: {root}")
        return

    warn_if_missing_pyproject_or_reqs(root)
    generate_requirements_if_missing(root)
    tar_project(root, output, user_excludes)

    print(f"[!] To base64 encode: base64 {output} > {output.with_suffix('.b64').name}")


if __name__ == "__main__":
    main()
