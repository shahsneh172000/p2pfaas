#!/bin/bash
CURRENT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

# shellcheck disable=SC1090
source "$CURRENT_PATH"/env/bin/activate
"$CURRENT_PATH"/env/bin/python "$CURRENT_PATH"/configure_scheduler.py \
  --host "192.168.1.251" \
  --scheduler "RoundRobinWithMasterScheduler true 192.168.1.251 true"
