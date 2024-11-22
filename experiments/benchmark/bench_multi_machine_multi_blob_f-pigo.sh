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

#
# Bench multiple values of the threshold, from $1 to $2
#

CURRENT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

# shellcheck disable=SC1090
source "$CURRENT_PATH"/env/bin/activate
"$CURRENT_PATH"/env/bin/python bench_multi_machine.py \
  --hosts-file "$CURRENT_PATH/hosts.txt" \
  --function-url "function/fn-pigo" \
  --payloads-dir "./blobs" \
  --payloads-list "family_50000bytes.jpg,family_100000bytes.jpg,family_200000bytes.jpg,family_300000bytes.jpg,family_400000bytes.jpg,family_500000bytes.jpg,family_600000bytes.jpg,family_700000bytes.jpg,family_800000bytes.jpg" \
  --requests "1000" \
  --start-lambda "2" \
  --end-lambda "3" \
  --lambda-delta "0.2" \
  --poisson

# family_900000bytes.jpg
