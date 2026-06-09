#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CHATRAW_DIR="${1:-"$ROOT_DIR/chatraw-fork"}"
PATCH_FILE="$ROOT_DIR/patches/chatraw-function1-function2.patch"

if [[ ! -d "$CHATRAW_DIR/.git" ]]; then
    echo "ChatRaw clone not found: $CHATRAW_DIR" >&2
    exit 1
fi

git -C "$CHATRAW_DIR" apply --binary "$PATCH_FILE"
echo "Applied CrossBridge Function 1, Function 2, Function 3, and Function 7 ChatRaw customizations."

# Vendored frontend libraries (Alpine, marked, PDF.js) are kept out of the patch and
# fetched + hash-verified here so the official-form viewer works fully offline.
python3 "$ROOT_DIR/scripts/sync_chatraw_vendor.py"
echo "Synced pinned ChatRaw vendor assets (Alpine, marked, PDF.js)."
