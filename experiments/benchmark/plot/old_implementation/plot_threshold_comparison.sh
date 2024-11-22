#!/bin/bash
#
# P2PFaaS - A framework for FaaS Load Balancing
# Copyright (c) 2019 - 2022. Gabriele Proietti Mattia <pm.gabriele@outlook.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

CURRENT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
FUNCTION_NAME="PigoFaceDetectF"
SERVER_DIR="BladeServers"
REQUESTS="20000reqs"

# shellcheck disable=SC1090
source "$CURRENT_PATH"/env/bin/activate

f=1

python plot_threshold_comparison.py \
  --path "/Users/gabrielepmattia/Coding/p2p-faas/experiments-data/$SERVER_DIR/$FUNCTION_NAME/LL-PS($f,K)/$REQUESTS/_8machines" \
  --function "Pigo Face Detect (F)" \
  --fanout $f \
  --from-threshold "0" \
  --to-threshold "10" \
  --job-duration "0.30" \
  -k "10" \
  --start-lambda "3.0" \
  --end-lambda "3.0" \
  --lambda-delta "0.1" \
  --n-machines "8"
