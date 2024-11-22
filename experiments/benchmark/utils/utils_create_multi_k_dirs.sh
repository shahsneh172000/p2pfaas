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

# shellcheck disable=SC1090
source "$CURRENT_PATH/../env/bin/activate"
"$CURRENT_PATH"/../env/bin/python "$CURRENT_PATH"/utils_create_multi_k_dirs.py \
  --out-dir "/Users/gabrielepmattia/Coding/p2p-faas/experiments-data/BladeServers/PigoFaceDetectF/LL-PS(1,K)/20000reqs-3" \
  --machines-n "8" \
  --fanout "1" \
  --threshold-from "0" \
  --threshold-to "10" \
  --algorithm-name "LL-PS"
