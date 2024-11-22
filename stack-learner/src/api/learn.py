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

import flask

import learners.learner
import log
from api.utils import Utils
from log import Log
from models import LearningEntry, ActEntry, ActOutput


class Learn:
    """
    The class Learn implements the methods used for performing the train
    """
    _MODULE_NAME = "api.Learn"

    @staticmethod
    def train_batch(request: flask.Request) -> bool:
        """
        Perform the train in batch, we expect a list of samples in the request
        """
        if not request.is_json:
            log.Log.merr(Learn._MODULE_NAME, "train_batch: request is not json")
            return False

        # parse each item
        req_json = request.get_json()

        if len(req_json) == 0:
            Log.merr(Learn._MODULE_NAME, "train_batch: request len is 0")
            return False

        learner = learners.learner.Learner.instance()

        for entry in req_json:

            try:
                eid_usable = int(entry["eid"])
                state_usable = list(map(lambda x: float(x), entry["state"].split(",")))
                action_usable = int(float(entry["action"]))
                reward_usable = float(entry["reward"])
            except Exception as e:
                Log.merr(Learn._MODULE_NAME,
                         f'train_batch: cannot cast learning entry: '
                         f'eid={entry["eid"]} '
                         f'state={entry["state"]} '
                         f'action={entry["action"]} '
                         f'reward={entry["reward"]}: {e}')
                return False

            learning_entry = LearningEntry()
            learning_entry.eid = eid_usable
            learning_entry.state = state_usable
            learning_entry.action = action_usable
            learning_entry.reward = reward_usable

            learner.train(learning_entry)

            Log.mdebug(Learn._MODULE_NAME, f"train_batch: training entry {learning_entry}")

        return True

    @staticmethod
    def train(request: flask.Request) -> bool:
        """
        Train a single learning entry
        """
        eid = None
        state = None
        action = None
        reward = None

        try:
            eid = request.headers[Utils.HEADER_LEARNING_EID]
            state = request.headers[Utils.HEADER_LEARNING_STATE]
            action = request.headers[Utils.HEADER_LEARNING_ACTION]
            reward = request.headers[Utils.HEADER_LEARNING_REWARD]
            Log.mdebug(Learn._MODULE_NAME, f"Passed eid={eid} state={state} action={action} reward={reward}")

        except Exception as e:
            Log.merr(Learn._MODULE_NAME, f"Cannot parse headers: e={e}")
            return False

        if state is None or action is None or reward is None or state == "" or action == "" or reward == "":
            Log.merr(Learn._MODULE_NAME, f"entry is not valid: state={state} action={action} reward={reward}")
            return False

        try:
            eid_usable = int(eid)
            state_usable = list(map(lambda x: float(x), state.split(",")))
            action_usable = int(float(action))
            reward_usable = float(reward)
        except Exception as e:
            Log.merr(Learn._MODULE_NAME,
                     f"cannot cast learning entry: eid={eid} state={state} action={action} reward={reward}: {e}")
            return False

        learner = learners.learner.Learner.instance()

        learning_entry = LearningEntry()
        learning_entry.eid = eid_usable
        learning_entry.state = state_usable
        learning_entry.action = action_usable
        learning_entry.reward = reward_usable

        learner.train(learning_entry)

        return True

    @staticmethod
    def act(request: flask.Request) -> (bool, ActOutput):
        """
        Decide the action according to the passed state
        """
        state = None

        try:
            state = request.headers[Utils.HEADER_LEARNING_STATE]
            Log.mdebug(Learn._MODULE_NAME, f"Passed state={state}")

        except Exception as e:
            Log.merr(Learn._MODULE_NAME, f"Cannot parse headers: e={e}")
            return False, 0.0

        if state is None or state == "":
            Log.merr(Learn._MODULE_NAME, f"entry is not valid: state={state}")
            return False, 0.0

        try:
            state_usable = list(map(lambda x: float(x), state.split(",")))
        except Exception as e:
            Log.merr(Learn._MODULE_NAME, f"cannot cast learning entry: state={state}: {e}")
            return False, 0.0

        learner = learners.learner.Learner.instance()

        act_entry = ActEntry()
        act_entry.state = state_usable

        result = learner.act(act_entry)

        return True, result
