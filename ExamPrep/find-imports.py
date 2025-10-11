# scripts/gen_instructions.py
import ast
import os
from pathlib import Path

# Hardcoded mapping of import names to PyPI packages
IMPORT_TO_PACKAGE = {
    "bs4": "beautifulsoup4",
    "yaml": "pyyaml",
    "cv2": "opencv-python",
    "PIL": "pillow",
    "lxml": "lxml",
    # add more if needed
}

# Known stdlib modules to ignore (partial list; use stdlib-list for full automation)
STDLIB_IGNORE = {
    "os", "sys", "re", "json", "time", "typing", "pathlib", "argparse", "subprocess",
    "base64", "http", "datetime", "shutil", "logging", "uuid", "threading", "asyncio",
    "secrets", "string", "__future__", "urllib", "random", "types"
}

INTERNAL_IGNORE = {
    "offsec_logger", "IdentityGenerator", "specs", "common", "file_transfer_server_logging"
}

COMMON_IGNORE = STDLIB_IGNORE | INTERNAL_IGNORE

project_dirs = ["machine-02" ,"machine-01", "common"]
found_imports = set()

for directory in project_dirs:
    for root, _, files in os.walk(directory):
        for f in files:
            if f.endswith(".py"):
                path = os.path.join(root, f)
                with open(path, encoding="utf-8") as src:
                    try:
                        tree = ast.parse(src.read(), filename=path)
                        for node in ast.walk(tree):
                            if isinstance(node, ast.Import):
                                for n in node.names:
                                    found_imports.add(n.name.split(".")[0])
                            elif isinstance(node, ast.ImportFrom) and node.module:
                                found_imports.add(node.module.split(".")[0])
                    except SyntaxError:
                        print(f"[!] Skipped syntax error in: {path}")

# Filter out common_ignore
third_party = sorted([
    IMPORT_TO_PACKAGE.get(mod, mod) for mod in found_imports if mod not in COMMON_IGNORE
])

# De-duplicate and sort
pkgs = sorted(set(third_party))

output = f"""# Setup Instructions

## 1. Create virtual environment

```bash
uv venv
```

## 2. Install dependencies

```bash
uv add {' '.join(pkgs)}
```

## 3. Compile locked requirements

```bash
uv pip compile --all-extras --output requirements.txt
```

## 4. Run the exploit PoC

```bash
python machine-01/main.py
```
"""

Path("Instruction.md").write_text(output)
print("[+] Instruction.md written with install steps.")
