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
REQUESTS="20000reqs-3"

# shellcheck disable=SC1090
source "$CURRENT_PATH"/env/bin/activate

f=1

#!/bin/bash
for i in {0..11}; do

  "$CURRENT_PATH"/env/bin/python plot_times.py --files-prefix "results-machine-" \
    --files-n "8" \
    --path "/Users/gabrielepmattia/Coding/p2p-faas/experiments-data/$SERVER_DIR/$FUNCTION_NAME/LL-PS($f,K)/$REQUESTS/LL-PS($f,$i)-8machines" \
    --function "Pigo Face Detect (F)" \
    --fanout $f \
    --threshold $i \
    --job-duration "0.30" \
    --with-model \
    --model-name "M/M/1/10" \
    -k "10" \
    --algorithm "LL-PS(F,T)"
  # --plot-every-machine

done
