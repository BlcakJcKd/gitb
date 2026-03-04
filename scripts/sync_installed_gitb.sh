#!/usr/bin/env bash
set -euo pipefail

SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC_FILE="$SRC_DIR/git_bulk.py"
DEST_FILE="${GITB_INSTALL_PATH:-/home/bivin/scripts/git_bulk.py}"

if [[ ! -f "$SRC_FILE" ]]; then
  echo "sync skipped: source file not found: $SRC_FILE"
  exit 0
fi

mkdir -p "$(dirname "$DEST_FILE")"
cp "$SRC_FILE" "$DEST_FILE"
chmod +x "$DEST_FILE"
echo "synced: $SRC_FILE -> $DEST_FILE"
