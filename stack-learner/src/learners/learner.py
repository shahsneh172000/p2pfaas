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

from learners.errors import ErrorsCodes, Errors
from learners.learner_sarsa_qtable import SarsaQTable
from learners.models import LearnerResponse
from log import Log
from models import LearningEntry, ActEntry


# noinspection PyAttributeOutsideInit
class Learner:
    _MODULE_NAME = "learners.Learner"
    _instance = None

    class Type(Enum):
        SARSA_QTABLE = "SarsaQTable"

    def __init__(self):
        raise RuntimeError('Call instance() instead')

    @classmethod
    def _init(cls, name="", parameters=None):
        cls._learning = None  # type: SarsaQTable or None
        cls._learning_type = None  # Learner.Type.SARSA_QTABLE  # type: Learner.Type

        # Log.minfo(Learner._MODULE_NAME, f"Init Learner: name={name} parameters={parameters}")

    #
    # Exported
    #

    def act(self, entry: ActEntry) -> LearnerResponse:
        """Implement the generic action decision from the state"""
        if self._learning_type == Learner.Type.SARSA_QTABLE:
            return self._learning.act(entry)

        return Errors.create_error(ErrorsCodes.ERROR_LEARNER_NOT_SUPPORTED)

    def train(self, entry: LearningEntry) -> LearnerResponse:
        """Implement the generic train step from state, action and reward"""
        Log.mdebug(Learner._MODULE_NAME, f"train: passed entry={entry}")

        if self._learning_type == Learner.Type.SARSA_QTABLE:
            return self._learning.train(entry)

        return Errors.create_error(ErrorsCodes.ERROR_LEARNER_NOT_SUPPORTED)

    def reset(self):
        """Restart learner ex-novo resetting parameters and value function/td form"""
        return self._learning.reset()

    def start(self):
        """Start the learner thread, if any"""
        self._learning.start()

    #
    # Exported -> Getters
    #

    def get_parameters(self) -> dict:
        return self._learning.get_parameters()

    def get_name(self) -> str:
        return self._learning_type.value

    def get_stats(self) -> dict:
        return self._learning.get_stats()

    def get_weights(self) -> dict:
        return self._learning.get_weights()

    #
    # Exported -> Setter
    #

    def set_learner(self, name="", parameters=None):
        if name == "" or name is None or name == Learner.Type.SARSA_QTABLE.value:
            self._learning = SarsaQTable(parameters_dict=parameters)
            self._learning_type = Learner.Type.SARSA_QTABLE
        else:
            Log.merr(Learner._MODULE_NAME, f"act: learning type '{name}' not supported, setting the default one")
            # stick to default
            self._learning = SarsaQTable(parameters_dict=parameters)
            self._learning_type = Learner.Type.SARSA_QTABLE

        Log.minfo(Learner._MODULE_NAME, f"Init Learner: name={name} parameters={parameters}")

    def set_parameters(self, new_parameters: dict) -> bool:
        return self._learning.set_parameters(new_parameters)

    @classmethod
    def instance(cls, learner="", parameters=None):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls._init(learner, parameters)
        return cls._instance
