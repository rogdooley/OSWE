#!/usr/bin/env bash
set -euo pipefail

# ================================
# Configurable Variables
# ================================

# Directory where user data (settings/extensions) will be stored
VSCODE_USER_DATA_DIR="/tmp/vscode-user-home"

# Project root to open in VS Code
PROJECT_DIR="/var/www/html"

# Port to bind code-server to (e.g., 8080)
PORT="10500"

# Optional password for code-server (leave blank for none)
PASSWORD=""

# ================================
# Setup
# ================================

# Ensure data dir exists
mkdir -p "$VSCODE_USER_DATA_DIR"

# Export HOME to sandbox VS Code settings (optional)
export HOME="$VSCODE_USER_DATA_DIR"

# Set password if specified
if [[ -n "$PASSWORD" ]]; then
    export PASSWORD="$PASSWORD"
fi

# ================================
# Launch code-server
# ================================
echo "[*] Launching VS Code Server on port $PORT"
echo "[*] User data dir: $VSCODE_USER_DATA_DIR"
echo "[*] Project dir: $PROJECT_DIR"

code-server \
    --port "$PORT" \
    --user-data-dir "$VSCODE_USER_DATA_DIR" \
    --auth none \
    "$PROJECT_DIR"