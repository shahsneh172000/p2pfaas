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

from functools import reduce
from typing import List

from log import Log


class QTable:
    _MODULE_NAME = "value_functions.QTable"

    def __init__(self, actions_n=1, alpha=0.01):
        self._actions_n = actions_n
        self._alpha = alpha

        self._actions_i_map = {}
        self._states_i_map = {}

        self._states_seen = 0
        self._actions_seen = 0

        # init the qtable
        self._table = []

        # init actions
        for action in range(self._actions_n):
            self._update_table_action(str(action))

        Log.minfo(QTable._MODULE_NAME, f"Init QTable for {self._actions_n} actions")

    def q_sa(self, state: List[float], action: float) -> float:
        usable_state, usable_action = self._normalize_state_action(state, action)
        self._update_table(usable_state, usable_action)

        return self._table[self._states_i_map[usable_state]][self._actions_i_map[usable_action]]

    def max_a_q_sa(self, state: List[float]):
        """Return the maximum value of Q for the action that maximizes it"""
        usable_state = self._normalize_state(state)
        self._update_table_state(usable_state)
        row_state = self._states_i_map[usable_state]

        max_value = self._table[row_state][0]
        max_action = 0

        for i in range(self._actions_n):
            if self._table[row_state][i] > max_value:
                max_value = self._table[row_state][i]
                max_action = i

        return max_value, max_action

    def train(self, state: List[float], action: float, delta: float):
        usable_state, usable_action = self._normalize_state_action(state, action)
        self._set(usable_state, usable_action, self.q_sa(state, action) + self._alpha * delta)

        # self._print_qtable()

    def get_weights(self):
        return {
            "actions_map": self._actions_i_map,
            "states_map": self._states_i_map,
            "table": self._table
        }

    #
    # Internals
    #

    def _normalize_state(self, state: List[float]) -> str:
        state_int = [str(int(s)) for s in state]
        usable_state = reduce(lambda x, y: str(x) + str(y), state_int)

        # Log.mdebug(QTable._MODULE_NAME, f"_normalize_state: input={state} output={usable_state}")

        return usable_state

    def _normalize_state_action(self, state: List[float], action: float) -> (str, str):
        usable_action = str(int(action))
        return self._normalize_state(state), usable_action

    def _update_table(self, state: str, action: str):
        self._update_table_state(state)
        self._update_table_action(action)

    def _update_table_state(self, state: str):
        if state not in self._states_i_map.keys():
            self._table.append([0.0 for _ in range(self._actions_n)])
            self._states_i_map[state] = self._states_seen
            self._states_seen += 1

    def _update_table_action(self, action: str):
        # Log.mdebug(QTable._MODULE_NAME, f"_update_table_action: for action={action}")

        if action not in self._actions_i_map.keys():

            if len(self._actions_i_map.keys()) == self._actions_n:
                raise RuntimeError("Exceeded number of actions")

            self._actions_i_map[action] = self._actions_seen
            self._actions_seen += 1

    def _set(self, state, action, value):
        self._update_table(state, action)
        self._table[self._states_i_map[state]][self._actions_i_map[action]] = value

    def _print_qtable(self):
        qtable_string = "\n\n"

        Log.mdebug(QTable._MODULE_NAME, f"_print_qtable: self._states_i_map={self._states_i_map}")
        Log.mdebug(QTable._MODULE_NAME, f"_print_qtable: self._actions_i_map={self._actions_i_map}")

        # print columns
        qtable_string += f"State\t"
        for action in range(self._actions_n):
            qtable_string += f"A{action}\t"
        qtable_string += "\n"

        for state in self._states_i_map.keys():
            qtable_string += f"{state}\t"
            for action in range(self._actions_n):
                Log.mdebug(QTable._MODULE_NAME,
                           f"_print_qtable: state={state} self._states_i_map[state]={self._states_i_map[state]}")
                Log.mdebug(QTable._MODULE_NAME,
                           f"_print_qtable: action={action} self._actions_i_map[str(action)]]={self._actions_i_map[str(action)]}")
                qtable_string += f"{self._table[self._states_i_map[state]][action]:.4f}\t"
            qtable_string += "\n"

        Log.mdebug(QTable._MODULE_NAME, qtable_string)
