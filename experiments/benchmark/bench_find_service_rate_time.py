#  P2PFaaS - A framework for FaaS Load Balancing
#  Copyright (c) 2019 - 2022. Gabriele Proietti Mattia <pm.gabriele@outlook.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

N_TESTS = 10
LAMBDA_MAX = 35.0  # 15.0
LAMBDA_MIN = 1.0  # 15.0
NUMBER_REQUESTS_PER_TEST = 500  # 1000

total_time = 0
for i in range(int(LAMBDA_MIN), int(LAMBDA_MAX)):
    print(f"Lambda: {i}")
    for j in range(N_TESTS):
        total_time += NUMBER_REQUESTS_PER_TEST / i

print(total_time / 3600)
