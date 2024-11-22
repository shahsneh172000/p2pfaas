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

from bellman_td_forms.qlearning import QLearning
from bellman_td_forms.sarsa_average_reward import SarsaAverageReward
from log import Log
from value_functions.value_function import ValueFunction


class TDForm:
    _MODULE_NAME = "bellman_td_forms.TDForm"

    class Type(Enum):
        Q_LEARNING = "q_learning"
        SARSA_AVERAGE_REWARD = "sarsa_average_reward"

    def __init__(self, td_form_type: Type, approximator: ValueFunction, parameters: List[float]):
        self._type = td_form_type
        self._td_form = None

        if self._type == TDForm.Type.SARSA_AVERAGE_REWARD:
            self._td_form = SarsaAverageReward(approximator, parameters[0])
        elif self._type == TDForm.Type.Q_LEARNING:
            self._td_form = QLearning(approximator, parameters[0])
        else:
            raise RuntimeError("TDForm not supported")

        Log.minfo(TDForm._MODULE_NAME, f"Init TDForm of type={self._type} parameters={parameters}")

    def delta(self, state: List[float], action: float, next_state: List[float], next_action: float, reward: float):
        if self._type == TDForm.Type.SARSA_AVERAGE_REWARD:
            return self._td_form.delta(state, action, next_state, next_action, reward)
        elif self._type == TDForm.Type.Q_LEARNING:
            return self._td_form.delta(state, action, next_state, next_action, reward)
        else:
            Log.merr(TDForm._MODULE_NAME, f"TDForm {self._type.name} is not supported")
            return 0.0
