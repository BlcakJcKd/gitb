#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

chmod +x "$REPO_ROOT/scripts/sync_installed_gitb.sh"
chmod +x "$REPO_ROOT/.githooks/post-commit"
chmod +x "$REPO_ROOT/.githooks/post-checkout"
chmod +x "$REPO_ROOT/.githooks/post-merge"

git -C "$REPO_ROOT" config core.hooksPath .githooks

echo "Installed local hooks path: $REPO_ROOT/.githooks"
echo "git_bulk.py will auto-sync to \${GITB_INSTALL_PATH:-/home/bivin/scripts/git_bulk.py}"
