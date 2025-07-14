# Offensive Security OSWE Utility Scripts

This repository contains a curated set of modular Python utilities developed in the context of the **Offensive Security OSWE (WEB-300)** course: *Advanced Web Attacks and Exploitation*. The tools are designed to support:

- Proof-of-concept exploit delivery
- Payload transfer and exfiltration
- Session manipulation and testing automation
- Course lab augmentation and CTF preparation

Each script is independently usable, minimal, and built with clarity, reuse, and demonstration in mind.

> For more details on the OSWE course: [OffSec WEB-300 FAQ](https://help.offsec.com/hc/en-us/articles/360046868971-WEB-300-Advanced-Web-Attacks-and-Exploitation-FAQ)

---

## `file_transfer_server.py`

A robust, configurable file upload/download server designed for delivering or receiving payloads during engagements.

### Features:
- Supports `GET`, `POST`, and base64 payloads
- Limits number of transfers
- Optional HTML landing page
- Logging to file/console with configurable level
- Dynamic route generation
- Graceful shutdown support

### Usage Example (Python API):
```python
from file_transfer_server import FileTransferServer

fts = FileTransferServer(
    file_path="loot.zip",
    save_dir="/tmp",
    direction="upload",
    limit=1,
    encoded=True,
    log_to_console=True,
    log_to_file=True,
    log_file_path="fts.log",
    enable_html_page=True,
    html_page_route='/transfer',
    on_transfer=lambda _path, _cnt: payload_served.set()
)
fts.start()
```

---

## `java_random.py`

Emulates Java's `java.util.Random` output stream in Python, used to predict PRNG values during deserialization or token analysis.

### Usage Example:
```python
from java_random import JavaRandom

r = JavaRandom(seed=12345)
print(r.next_int(100))  # Emulates Java's nextInt(100)
```

---

## `load_session_cookie.py`

Loads a saved session cookie from disk and injects it into a `requests.Session` object for authenticated reuse.

### Usage Example:
```python
from load_session_cookie import load_cookie

session = load_cookie("session_cookie.json")
resp = session.get("https://target.com/account")
```

---

## `save_session_cookie.py`

Extracts session cookies from a `requests.Session` and stores them on disk as JSON.

### Usage Example:
```python
from save_session_cookie import save_cookie
import requests

session = requests.Session()
session.post("https://target.com/login", data={"u": "a", "p": "b"})
save_cookie(session, "session_cookie.json")
```

---

## `payload_listener.py`

Lightweight HTTP server that prints POSTed payloads to console—used to receive exfiltrated or beacon data.

### Command Line Usage:
```bash
python3 payload_listener.py 8080
```

### Python Usage:
```python
from payload_listener import start_listener
start_listener(port=8080)
```

> Displays a startup banner for visual confirmation.

---

## `serve_once.py`

Single-use HTTP file server. Serves one file to one client then exits. Useful for payload drops where stealth is required.

### Command Line Usage:
```bash
python3 serve_once.py secret.zip
```

---

## Notes

- These scripts are designed for modular integration.
- All scripts support Python 3.8+.
- Logging, cleanup, and shutdown behaviors are included where applicable.

---

## Contributing

These utilities were developed as part of personal research and development during the **Offensive Security OSWE (WEB-300)** course. While this is not a formal open-source package, feedback and suggestions are welcome.

You are encouraged to:
- Report bugs or unexpected behavior
- Suggest enhancements or cleaner implementations
- Submit focused pull requests that maintain simplicity and usefulness in PoC development

Please:
- Keep compatibility with Python 3.8+
- Maintain clear logging, minimal dependencies, and low friction usage

---

## Integrating with Your PoCs

These scripts are designed to be embedded into larger PoC scripts or lab environments with minimal modification.

Examples of use:
- `FileTransferServer` can be started within an exploit to serve or receive files dynamically
- Session utilities help preserve authenticated contexts for tools that reuse `requests.Session`
- `payload_listener` is ideal for blind data capture during injection testing

Scripts are intentionally kept lightweight, modular, and self-contained to support:
- Integration with exploit workflows
- Custom automation for CTFs, bug bounties, or client demos
- Rapid adaptation during offensive testing exercises

---

## `offsec_logger.py`

A lightweight, colorized logger tailored for Offensive Security WEB-300 workflows and exploit scripts.

Features:
	•	Logging indicators: [+], [!], [*], [?], [-], [~], [>]
	•	Colorized terminal output (Linux/macOS compatible)
	•	Optional log file output (e.g. exploit.log) without ANSI color codes
	•	Debug mode with full timestamps
	•	Automatic stage/step timers for tracking elapsed time
	•	.custom() method for advanced formatting or custom indicators

Indicator Summary:

Symbol	Meaning
[+]	Success / Positive result
[!]	Error / Critical issue
[*]	General info / Action log
[?]	User input / Prompt
[-]	Negation / Skipped / Removed
[~]	Passive state / Waiting
[>]	Instruction / Step in progress


⸻

Usage Example

from offsec_logger import OffsecLogger
import time

log = OffsecLogger(log_file="exploit.log", debug=True)

log.info("Launching exploit")
log.stage("User enumeration")
time.sleep(1.5)
log.success("Found valid user: alice")

log.stage("Magic link brute force")
time.sleep(2.2)
log.error("Token window too small")

log.custom("[~]", "Retrying with wider time window")
log.success("Token accepted")

Example Output (stdout)

[12:41:03] [*] Launching exploit
[12:41:03] [>] Starting: User enumeration
[12:41:04] [+] Found valid user: alice (1.50s)
[12:41:04] [>] Starting: Magic link brute force
[12:41:06] [!] Token window too small (2.20s)
[12:41:06] [~] Retrying with wider time window
[12:41:06] [+] Token accepted

API Overview

log = OffsecLogger(
    log_file="exploit.log",   # Optional path to write clean log output
    debug=True                # If True, adds timestamps and durations
)

log.info(msg)       # [*] Information
log.success(msg)    # [+] Success
log.error(msg)      # [!] Error
log.warn(msg)       # [-] Warning or skipped
log.prompt(msg)     # [?] Prompt or question
log.waiting(msg)    # [~] Passive state or sleep
log.action(msg)     # [>] Ongoing action
log.stage(name)     # Tracks duration of a named stage (calls action internally)
log.custom(sym, msg)# Custom symbol and message


⸻



## License

This project is intended for lawful security testing, research, and education only.
