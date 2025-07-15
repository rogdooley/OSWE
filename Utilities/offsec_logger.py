import logging
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Optional

class OffsecLogger:
    """
    OffsecLogger

    Author: Roger Dooley
    Created for: Offensive Security OSWE (WEB-300) coursework and PoC development

    Custom logging utility for OSWE PoC scripting.
    Provides colorized console output with exploit-centric symbols and optional file logging.

    Indicators:
        [*] - Info (Blue)
        [+] - Success (Green)
        [-] - Error (Red)
        [!] - Warning (Yellow)
        [!] - Critical (Bright Red)
        [DEBUG] - Debug messages with timestamps

    Usage:
        logger = OffsecLogger("exploit.log")
        logger.info("Starting exploit")
        logger.success("Exploit successful")
        logger.error("Something failed")
        logger.start_timer("stage1")
        logger.success("Stage complete", timer="stage1")

    Supports optional log-to-file while printing colorized stdout.
    """

    COLOR_RESET = "\033[0m"
    COLORS = {
        "INFO": "\033[94m",
        "SUCCESS": "\033[92m",
        "WARNING": "\033[93m",
        "ERROR": "\033[91m",
        "CRITICAL": "\033[91;1m",
        "DEBUG": "\033[90m"
    }

    SYMBOLS = {
        "INFO": "[*]",
        "SUCCESS": "[+]",
        "WARNING": "[!]",
        "ERROR": "[-]",
        "CRITICAL": "[!]",
        "DEBUG": "[DEBUG]"
    }

    def __init__(self, logfile: Optional[str] = None, debug: bool = False):
        self.logfile = Path(logfile).resolve() if logfile else None
        self.debug_mode = debug
        self.timers = {}

        if self.logfile:
            self.logfile.parent.mkdir(parents=True, exist_ok=True)
            with self.logfile.open("w") as f:
                f.write("")  # clear existing

    def _write(self, level: str, message: str):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        symbol = self.SYMBOLS.get(level, "[*]")
        color = self.COLORS.get(level, "")
        reset = self.COLOR_RESET

        out = f"{symbol} {message}"
        colored = f"{color}{symbol} {message}{reset}"

        print(colored)

        if self.logfile:
            with self.logfile.open("a") as f:
                f.write(f"[{ts}] {out}\n")

    def info(self, msg: str):
        self._write("INFO", msg)

    def success(self, msg: str, timer: Optional[str] = None):
        if timer and timer in self.timers:
            elapsed = time.time() - self.timers[timer]
            msg = f"{msg} (elapsed: {elapsed:.2f}s)"
        self._write("SUCCESS", msg)

    def warning(self, msg: str):
        self._write("WARNING", msg)

    def error(self, msg: str):
        self._write("ERROR", msg)

    def critical(self, msg: str):
        self._write("CRITICAL", msg)

    def debug(self, msg: str):
        if self.debug_mode:
            ts = datetime.now().strftime("%H:%M:%S")
            self._write("DEBUG", f"[{ts}] {msg}")

    def start_timer(self, label: str):
        self.timers[label] = time.time()

    def end_timer(self, label: str):
        if label in self.timers:
            elapsed = time.time() - self.timers[label]
            del self.timers[label]
            return elapsed
        return None

