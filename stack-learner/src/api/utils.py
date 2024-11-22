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

import json

import flask


class Utils:
    """
    Implements useful methods for the package
    """
    HEADER_LEARNING_EID = "X-P2pfaas-Learning-Eid"
    HEADER_LEARNING_STATE = "X-P2pfaas-Learning-State"
    HEADER_LEARNING_ACTION = "X-P2pfaas-Learning-Action"
    HEADER_LEARNING_REWARD = "X-P2pfaas-Learning-Reward"

    HEADER_EPSILON = "X-P2pfaas-Eps"

    @staticmethod
    def prepare_res_json(response: dict) -> flask.Response:
        """
        Prepare the json for the request
        """
        res_str = json.dumps(response)

        res = flask.Response(res_str)
        res.headers['Content-Type'] = 'application/json'

        return res

    @staticmethod
    def prepare_res(status_code: int, headers: dict = None, content_str: str = "") -> flask.Response:
        """
        Prepare the response
        """
        res = flask.Response(content_str)
        res.status_code = status_code

        if headers is not None:
            for header_key in headers.keys():
                res.headers.add(header_key, headers[header_key])

        return res
