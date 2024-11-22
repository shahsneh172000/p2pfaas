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

import matplotlib.pyplot as plt

MI = 1 / 0.180
MIN_LAMBDA = 1
MAX_LAMBDA = 35.0

N_SERVERS = 3
QUEUE_LEN = 0


def erlang_b(load, n_servers):
    inv = 1
    for m in range(1, n_servers + 1):  # range does not include the last number, so we need to add 1
        inv = 1 + m / load * inv
    return 1 / inv


def y(lam, mi, k) -> float:
    rho = lam / mi

    k_fact = k
    for i in range(1, k):
        k_fact *= k - i

    num = pow(rho, k) / k_fact

    den = 0
    for j in range(k + 1):
        j_fact = 1
        if j > 0:
            j_fact = j
            for m in range(1, j):
                j_fact *= j - m

        den += pow(lam, j) * (1 / j_fact)

    return num / den


X = []
Y = []

for lam in range(int(MIN_LAMBDA), int(MAX_LAMBDA)):
    X.append(lam)
    # Y.append(y(lam, MI, N_SERVERS))
    Y.append(erlang_b(lam, N_SERVERS))

plt.plot(X, Y)
plt.show()
