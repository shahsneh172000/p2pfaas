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
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.
from typing import List

from log import Log
from value_functions.value_function import ValueFunction


class QLearning:
    _MODULE_NAME = "bellman_td_forms.QLearning"

    def __init__(self, approximator: ValueFunction, gamma=0.01):
        self._approximator = approximator

        self._gamma = gamma

        Log.minfo(QLearning._MODULE_NAME, f"Init QLearning with gamma={gamma}")

    def delta(self, state: List[float], action: float, next_state: List[float], next_action: float, reward: float):
        delta_value = reward \
                      + self._gamma * self._approximator.max_a_q_sa(next_state) \
                      - self._approximator.q_sa(state, action)

        return delta_value
