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
"$CURRENT_PATH"/env/bin/python bench_single_machine.py \
  --host "192.168.1.61:18080" \
  --function-url "function/pigo-face-detector-f" \
  --start-lambda "2.0" \
  --end-lambda "3.4" \
  --lambda-delta "0.1" \
  --requests "5000" \
  --poisson

#  -p "/Users/gabry3795/Coding/p2p-fog/experiments/benchmark/blobs/family.jpg" \