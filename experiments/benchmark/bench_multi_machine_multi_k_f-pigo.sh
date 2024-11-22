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

echo "=== Starting loop from T=$1 to T=$2 ==="

for ((i = $1; i <= $2; i++)); do
  echo "=> Setting T=$i"
  "$CURRENT_PATH"/../machines-setup/python_scripts/configure_scheduler.sh $i
  sleep 30
  echo "=> Starting test with T=$i"
  "$CURRENT_PATH"/bench_multi_machine_f-pigo.sh
  sleep 300
done
