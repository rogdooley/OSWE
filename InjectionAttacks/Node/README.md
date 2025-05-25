# Blind Command Injection Exploit (Time-Based)

This Python script performs time-based blind command injection against a vulnerable web application where user input is executed via `eval()` in Node.js. It infers command output one character at a time by measuring response delays.

## Features

- Interactive extraction of command output (e.g., `/flag.txt`)
- Uses timing side-channels (e.g., `sleep`) to detect correct characters
- Character-by-character enumeration
- Configurable timing parameters
- Supports HTB-like challenge targets

## Usage

### Command

```bash
python3 exploit.py --target http://<host>:<port> --email <email> [--sleep <seconds>] [--threshold <seconds>]
```