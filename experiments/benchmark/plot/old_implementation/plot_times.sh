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
source "$CURRENT_PATH"/env/bin/activate

k=10
T=5

source "$CURRENT_PATH"/env/bin/activate
"$CURRENT_PATH"/env/bin/python plot_times.py --files-prefix "results-machine-" \
  --files-n "5" \
  --path "../_bench_multi_machine-10192020-172642" \
  --function "Pigo Face Detect (F)" \
  --fanout "1" \
  --job-duration "0.30" \
  --model-name "M/M/1/$k" \
  -k $k \
  --algorithm "NS(K)" \
  --threshold $T

  # --with-model \
