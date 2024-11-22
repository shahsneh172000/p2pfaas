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

from functools import reduce

from matplotlib import pyplot as plt


class MM1K:
    @staticmethod
    def p_i(l, mi, i, k):
        """Compute the probability of the system to be in the state i"""
        ro = float(l) / float(mi)
        k = int(k)
        if ro == 1.0:
            ro -= 0.00001
        return ((1 - ro) / (1 - pow(ro, k + 1))) * pow(ro, i)

    @staticmethod
    def P_B(l, mi, k):
        """Compute the blocking probability"""
        return MM1K.p_i(l, mi, k, k)

    @staticmethod
    def delay(l, mi, k):
        k = int(k)

        num = reduce(lambda x, y: x + y, [i * MM1K.p_i(l, mi, i, k) for i in range(0, k + 1)])
        den = l * (1 - MM1K.P_B(l, mi, k))
        return num / den

    @staticmethod
    def newDelay(l, mi, k):
        ro = float(l) / float(mi)
        k = int(k)

        return (1 / (mi - l)) - ((k * pow(ro, k + 1)) / (l * (1 - pow(ro, k))))

    @staticmethod
    def generatePbArray(lambda_array, k, mi):
        out = []
        for l in lambda_array:
            out.append(MM1K.P_B(l, mi, k))
        return out

    @staticmethod
    def generateDelayArray(lambda_array, k, mi):
        out = []
        for l in lambda_array:
            out.append(MM1K.delay(l, mi, k))
        return out

    @staticmethod
    def generateDelayArrayNew(lambda_array, k, mi):
        out = []
        for l in lambda_array:
            out.append(MM1K.newDelay(l, mi, k))
        return out


#  print(P_B(0.8, 1, 10))

MI = 2
MIN_LAMBDA = 0.1
MAX_LAMBDA = 4.0
LAMBDA_DELTA = 0.1
QUEUE_LEN = 4

X = []
Y = []

current_lambda = MIN_LAMBDA
while True:
    print(current_lambda)

    X.append(current_lambda)
    Y.append(MM1K.delay(current_lambda, MI, QUEUE_LEN))

    current_lambda = round(current_lambda + LAMBDA_DELTA, 2)
    if current_lambda > MAX_LAMBDA:
        break

plt.plot(X, Y)
plt.show()
