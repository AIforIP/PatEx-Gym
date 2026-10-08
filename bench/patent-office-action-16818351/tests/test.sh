#!/bin/bash
set -euo pipefail
mkdir -p /logs/verifier
unset LD_PRELOAD || true
unset FAKETIME || true
unset FAKETIME_DONT_FAKE_MONOTONIC || true

write_fallback_reward() {
  local reason="$1"
  python3 - "$reason" <<'PY'
import json, sys
from pathlib import Path
reason = sys.argv[1]
log_dir = Path('/logs/verifier')
log_dir.mkdir(parents=True, exist_ok=True)
report = {
    'reward': 0.0,
    'completion_score': 0.0,
    'error': reason,
    'trajectory_scoring_weight': 0.0,
}
(log_dir / 'reward.json').write_text(json.dumps(report, indent=2) + '\n')
(log_dir / 'reward.txt').write_text('0.0\n')
(log_dir / 'evaluation_report.md').write_text(
    f'# Patent Agent Evaluation v2 Report\n\nVerifier fallback: {reason}\n'
)
PY
}

if [ -f /tests/verify_outputs.py ]; then
  python3 /tests/verify_outputs.py || write_fallback_reward "verify_outputs.py failed"
elif [ -f ./verify_outputs.py ]; then
  python3 ./verify_outputs.py || write_fallback_reward "verify_outputs.py failed"
else
  write_fallback_reward "verify_outputs.py not found"
fi
