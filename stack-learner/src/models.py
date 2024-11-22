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

import dataclasses
from typing import List


@dataclasses.dataclass(init=False)
class LearningEntry:
    eid: int

    state: List[float]
    action: float

    reward: float


@dataclasses.dataclass(init=False)
class ActEntry:
    state: List[float]


@dataclasses.dataclass(init=False)
class ActOutput:
    action: float
    eps: float


@dataclasses.dataclass(init=False)
class APIError:
    code: int
    status: int
    message: str


@dataclasses.dataclass(init=False)
class ParametersLearner:
    name: str
    parameters: dict

    def to_dict(self):
        return {
            "name": self.name,
            "parameters": self.parameters
        }
