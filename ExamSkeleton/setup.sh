#!/usr/bin/env bash
set -euo pipefail

# setup.sh - Prepares the Python project structure
# Adds __init__.py files to all directories under ./common/

echo "[*] Creating __init__.py files under common/"
find common -type d -exec touch {}/__init__.py \;

echo "[*] Done. Package structure is now recognized by Python."