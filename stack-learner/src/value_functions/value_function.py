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

from enum import Enum
from typing import List

from log import Log
from value_functions.qtable import QTable


class ValueFunction:
    _MODULE_NAME = "value_functions.ValueFunction"

    class Type(Enum):
        TYPE_QTABLE = "qtable"

    def __init__(self, value_function_type: Type, actions_n=1, parameters=()):
        self._value_function_type = value_function_type
        self._value_function = None

        # init value_function_type type
        if self._value_function_type == ValueFunction.Type.TYPE_QTABLE:
            self._value_function = QTable(actions_n=actions_n, alpha=parameters[0])
        else:
            raise RuntimeError("ValueFunction used is not supported")

        Log.minfo(ValueFunction._MODULE_NAME, f"Init ValueFunction of "
                                              f"type={self._value_function_type} "
                                              f"actions_n={actions_n} "
                                              f"parameters={parameters}")

    def train(self, state: List[float], action: float, delta: float):
        if self._value_function_type == ValueFunction.Type.TYPE_QTABLE:
            self._value_function.train(state, action, delta)
        else:
            raise RuntimeError(f"ValueFunction type {self._value_function_type} does not support train")

    def q_sa(self, state: List[float], action: float):
        if self._value_function_type == ValueFunction.Type.TYPE_QTABLE:
            return self._value_function.q_sa(state, action)
        else:
            raise RuntimeError(f"ValueFunction type {self._value_function_type} does not support q_sa")

    #
    # Utils
    #

    def max_a_q_sa(self, state):
        """Returns the Q value and the action index for the action that maximizes it given the state"""
        return self._value_function.max_a_q_sa(state)

    def get_weights(self):
        return self._value_function.get_weights()