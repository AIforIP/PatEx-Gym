#!/bin/bash
set -euo pipefail

if [ -x /usr/bin/codex ]; then
    codex_bin=/usr/bin/codex
elif [ -x /opt/patex-apply-patch/codex ]; then
    codex_bin=/opt/patex-apply-patch/codex
else
    echo "apply_patch: compatible Codex patch engine is unavailable" >&2
    exit 127
fi

if [ "$#" -eq 0 ]; then
    patch_text="$(cat)"
elif [ "$#" -eq 1 ]; then
    patch_text="$1"
else
    echo "Usage: apply_patch [PATCH]; or provide PATCH on stdin" >&2
    exit 2
fi

exec "$codex_bin" --codex-run-as-apply-patch "$patch_text"
