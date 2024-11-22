#!/bin/bash
CURRENT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

# usage: configure_scheduler.sh THRESHOLD TAU
#        configure_scheduler.sh 5 100ms

# shellcheck disable=SC1090
source "$CURRENT_PATH"/env/bin/activate
"$CURRENT_PATH"/env/bin/python "$CURRENT_PATH"/configure_scheduler.py \
  --hosts-file "$CURRENT_PATH"/hosts.txt \
  --scheduler "PowerOfNSchedulerTau 1 $1 true 1 $2"
