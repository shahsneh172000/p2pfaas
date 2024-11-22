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

echo "=== Starting loop from tau=$1 to tau=$2, delta_tau=$3, T=$4 ==="

for ((tau = $1; tau <= $2; tau = tau + $3)); do
  echo "=> Setting tau=$tau"
  "$CURRENT_PATH"/../machines-setup/python_scripts/configure_pwr_n_tau_scheduler.sh "$4" "${tau}ms"
  sleep 15
  echo "=> Starting test with tau=$tau"
  "$CURRENT_PATH"/bench_multi_machine_f-pigo.sh
  sleep 60
done
