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
"$CURRENT_PATH"/env/bin/python plot_times_distribution.py --files-prefix "req-times-" \
  --path "/Users/gabry3795/Cloud/Google Drive/Università/Magistrale/Thesis/Experiments/BladeServers/PigoFaceDetect/MultiNode/LL(1,K-9)-8machines/_test_multi_machine-04072019-085332" \
  --function "Pigo Face Detect" \
  --fanout "1" \
  --threshold "9" \
  --job-duration "0.274371" \
  -k "10" \
  --start-lambda "0.1" \
  --end-lambda "3.80" \
  --lambda-delta "0.05" \
  --bins "30" \
  --machine-id "0"
#                        --data-files "/Users/gabry3795/Cloud/Google Drive/Università/Magistrale/Thesis/Data/BladeServers/MultiNode/Loop/LL(1,K-2)-16machines-heat/_test_multi_machine-03302019-163137:/Users/gabry3795/Cloud/Google Drive/Università/Magistrale/Thesis/Data/BladeServers/SingleNode/Loop/NS(K10)-heat/_test_multi_get-03302019-114919"
