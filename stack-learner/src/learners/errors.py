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

from learners.models import LearnerResponse


class ErrorsCodes(Enum):
    ERROR_LEARNER_NOT_SUPPORTED = 0
    ERROR_TRAIN_ENTRY_ALREADY_IN_LIST = 1


class ErrorMessages:
    _ERROR_MESSAGES = {
        ErrorsCodes.ERROR_LEARNER_NOT_SUPPORTED: "Learner is not supported",
        ErrorsCodes.ERROR_TRAIN_ENTRY_ALREADY_IN_LIST: "Passed train entry is already in list"
    }

    @staticmethod
    def get(code: ErrorsCodes) -> str:
        return ErrorMessages._ERROR_MESSAGES[code]


class Errors:

    @staticmethod
    def create_error(error_code: ErrorsCodes) -> LearnerResponse:
        res = LearnerResponse()
        res.error = True
        res.error_code = error_code
        res.error_message = ErrorMessages.get(error_code)

        return res
