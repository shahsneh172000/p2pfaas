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
import random
import threading
from typing import List

from bellman_td_forms.td_form import TDForm
from learners.errors import Errors, ErrorsCodes
from learners.models import LearnerResponse
from log import Log
from models import LearningEntry, ActEntry
from value_functions.value_function import ValueFunction


class SarsaQTable:
    _MODULE_NAME = "learners.SarsaQTable"

    PARAM_ACTIONS_N = "actions_n"
    PARAM_ALPHA = "alpha"
    PARAM_BETA = "beta"
    PARAM_WINDOW_SIZE = "window_size"
    PARAM_EPSILON_START = "epsilon_start"
    PARAM_EPSILON_MIN = "epsilon_min"
    PARAM_EPSILON_DECAY = "epsilon_decay"
    PARAM_EPSILON_DECAY_ENABLED = "epsilon_decay_enabled"
    PARAM_ENTRY_MISSING_MAX_ATTEMPTS = "entry_missing_max_attempts"  # max check_trainable missing job

    def __init__(self, actions_n=2,
                 alpha=0.01,
                 beta=0.01,
                 window_size=5,
                 epsilon_start=0.9,
                 epsilon_min=0.1,
                 epsilon_decay=0.99,
                 epsilon_decay_enabled=True,
                 entry_missing_max_attempts=100,
                 parameters_dict=None
                 ):

        self._alpha = alpha
        self._beta = beta
        self._window_size = window_size
        self._actions_n = actions_n

        self._epsilon_start = epsilon_start
        self._epsilon_min = epsilon_min
        self._epsilon_decay = epsilon_decay
        self._epsilon_decay_enabled = epsilon_decay_enabled
        self._entry_missing_max_attempts = entry_missing_max_attempts

        # parameters dict overrides all
        if parameters_dict is not None:
            self.set_parameters(parameters_dict)

        # init learning
        self._epsilon = epsilon_start
        self._value_function = None
        self._td_form = None

        self._init_learning()

        # init runtime vars
        self._list_entries = []  # type: List[LearningEntry]

        self._entry_missing_attempts = {}  # { "id": attempts }
        """Max attempts before removing"""

        # locks
        self._lock_empty = None  # max items in queue
        self._lock_filled = None
        self._lock_cs = None  # for the self._list_entries

        # counters
        self._counter_inferences = 0
        self._counter_trained_items = 0
        self._counter_episodes = 0

        self._eid_latest_trained = 0
        self._eid_max_seen = 0

        # looper thread
        self._thread_looper = None
        self._thread_interrupt = False

        Log.minfo(SarsaQTable._MODULE_NAME, f"Init SarsaQTable with alpha={alpha} "
                                            f"beta={beta} "
                                            f"window_size={window_size} "
                                            f"eps={epsilon_start}")

    #
    # Exported
    #

    def train(self, entry: LearningEntry) -> LearnerResponse:
        Log.mdebug(SarsaQTable._MODULE_NAME, "train: adding entry")

        # wait for space in the buffer
        self._lock_empty.acquire()

        # critical section of list items
        self._lock_cs.acquire()

        # check if entry eid already in list, skip if yes
        if self._check_if_eid_in_list(entry.eid):
            Log.merr(SarsaQTable._MODULE_NAME, f"train: entry eid={entry.eid} already in list, skipping")
            self._lock_cs.release()
            return Errors.create_error(ErrorsCodes.ERROR_TRAIN_ENTRY_ALREADY_IN_LIST)

        # add data, re-sort according req id
        self._list_entries.append(entry)
        self._list_entries = sorted(self._list_entries, key=lambda item: item.eid)

        Log.mdebug(SarsaQTable._MODULE_NAME, f"train: sorted {len(self._list_entries)} entries")
        self._print_entries_list()

        self._lock_cs.release()

        # add to empty sem
        self._lock_filled.release()

        return LearnerResponse()

    def act(self, entry: ActEntry) -> LearnerResponse:
        """Returns the action that maximizes the q_sa"""
        if random.random() < self._epsilon:
            action = random.randint(0, self._actions_n - 1)
        else:
            action = self._value_function.max_a_q_sa(entry.state)[1]

        output = LearnerResponse()
        output.action = action
        output.eps = self._epsilon

        # update epsilon
        if self._epsilon > self._epsilon_min and self._epsilon_decay_enabled:
            self._epsilon *= self._epsilon_decay

        self._counter_inferences += 1

        return output

    def reset(self):
        self._counter_inferences = 0
        self._counter_trained_items = 0
        self._counter_episodes = 0
        self._epsilon = self._epsilon_start

        self._init_learning()
        self._init_learner()

    def start(self):
        """Start the learner thread, if any"""
        self._init_learner()
        Log.minfo(SarsaQTable._MODULE_NAME, f"Started SarsaQTable")

    #
    # Exported -> Getter
    #

    def get_parameters(self) -> dict:
        return {
            SarsaQTable.PARAM_ACTIONS_N: self._actions_n,
            SarsaQTable.PARAM_ALPHA: self._alpha,
            SarsaQTable.PARAM_BETA: self._beta,
            SarsaQTable.PARAM_WINDOW_SIZE: self._window_size,
            SarsaQTable.PARAM_EPSILON_START: self._epsilon_start,
            SarsaQTable.PARAM_EPSILON_MIN: self._epsilon_min,
            SarsaQTable.PARAM_EPSILON_DECAY: self._epsilon_decay,
            SarsaQTable.PARAM_EPSILON_DECAY_ENABLED: self._epsilon_decay_enabled,
            SarsaQTable.PARAM_ENTRY_MISSING_MAX_ATTEMPTS: self._entry_missing_max_attempts,
        }

    def get_stats(self) -> dict:
        self._lock_cs.acquire()
        pending_entries = len(self._list_entries)
        self._lock_cs.release()

        return {
            "inferences": self._counter_inferences,
            "trained_items": self._counter_trained_items,
            "epsilon": self._epsilon,
            "episodes": self._counter_episodes,
            "pending_entries": pending_entries,
            "eid_max_seen": self._eid_max_seen,
            "eid_last_trained": self._eid_latest_trained
        }

    def get_weights(self) -> dict:
        self._lock_cs.acquire()
        weights = self._value_function.get_weights()
        self._lock_cs.release()

        return weights

    #
    # Exporter -> Setters
    #

    def set_parameters(self, new_parameters: dict) -> bool:
        if new_parameters is None:
            return False

        new_parameters_keys = new_parameters.keys()

        if SarsaQTable.PARAM_ACTIONS_N in new_parameters_keys:
            self._actions_n = new_parameters[SarsaQTable.PARAM_ACTIONS_N]

        if SarsaQTable.PARAM_ALPHA in new_parameters_keys:
            self._alpha = float(new_parameters[SarsaQTable.PARAM_ALPHA])

        if SarsaQTable.PARAM_BETA in new_parameters_keys:
            self._beta = float(new_parameters[SarsaQTable.PARAM_BETA])

        if SarsaQTable.PARAM_WINDOW_SIZE in new_parameters_keys:
            self._window_size = int(new_parameters[SarsaQTable.PARAM_WINDOW_SIZE])

        if SarsaQTable.PARAM_ENTRY_MISSING_MAX_ATTEMPTS in new_parameters_keys:
            self._entry_missing_max_attempts = int(new_parameters[SarsaQTable.PARAM_ENTRY_MISSING_MAX_ATTEMPTS])

        if SarsaQTable.PARAM_EPSILON_START in new_parameters_keys:
            self._epsilon_start = float(new_parameters[SarsaQTable.PARAM_EPSILON_START])

        if SarsaQTable.PARAM_EPSILON_MIN in new_parameters_keys:
            self._epsilon_min = float(new_parameters[SarsaQTable.PARAM_EPSILON_MIN])

        if SarsaQTable.PARAM_EPSILON_DECAY in new_parameters_keys:
            self._epsilon_decay = float(new_parameters[SarsaQTable.PARAM_EPSILON_DECAY])

        if SarsaQTable.PARAM_EPSILON_DECAY_ENABLED in new_parameters_keys:
            self._epsilon_decay_enabled = bool(new_parameters[SarsaQTable.PARAM_EPSILON_DECAY_ENABLED])

        return True

    #
    # Internals
    #

    def _init_learner(self):
        self._list_entries = []  # type: List[LearningEntry]

        self._entry_missing_attempts = {}  # { "id": attempts }
        """Max attempts before removing"""

        # counters
        self._counter_inferences = 0
        self._counter_trained_items = 0
        self._counter_episodes = 0

        self._eid_latest_trained = 0
        self._eid_max_seen = 0

        # interrupt old thread
        if self._thread_looper is not None:
            self._thread_interrupt = True
            # release the lock if locked
            self._lock_filled.release()
            # wait for termination
            self._thread_looper.join()
            # reset
            self._thread_interrupt = False

        # locks
        self._lock_empty = threading.Semaphore(10000)  # max items in queue
        self._lock_filled = threading.Semaphore(0)
        self._lock_cs = threading.Semaphore(1)  # for the self._list_entries

        # start new thread
        self._thread_looper = threading.Thread(target=self._looper)
        self._thread_looper.start()

    def _init_learning(self):
        self._epsilon = self._epsilon_start

        self._value_function = ValueFunction(
            ValueFunction.Type.TYPE_QTABLE,
            actions_n=self._actions_n,
            parameters=[self._alpha]
        )

        self._td_form = TDForm(
            TDForm.Type.SARSA_AVERAGE_REWARD,
            self._value_function,
            parameters=[self._beta]
        )

    def _looper(self):
        Log.minfo(SarsaQTable._MODULE_NAME, "_looper: started thread, waiting for learning entries...")

        """The loop process the training for every new entry"""
        while True:
            # wait for new learning entries
            self._lock_filled.acquire()
            Log.mdebug(SarsaQTable._MODULE_NAME, "_looper: entry available")

            if self._thread_interrupt:
                Log.minfo(SarsaQTable._MODULE_NAME, "_looper: exiting thread")
                break

            # process the first entry, critical
            self._lock_cs.acquire()

            # check if window can be trained
            trainable = self._check_trainable_episode()
            if trainable:
                Log.mdebug(SarsaQTable._MODULE_NAME, "_looper: starting train")
                self._train_window()

            Log.mdebug(SarsaQTable._MODULE_NAME, f"_looper: trainable={trainable}")

            self._lock_cs.release()

    def _check_trainable_episode(self):
        """Check if we have {window_size contiguous}"""
        # skip the check if the length of the list is less than window size
        if len(self._list_entries) < self._window_size:
            return False

        starting_eid = self._list_entries[0].eid - 1
        expected_eid = starting_eid

        current_i = -1
        trainable = True

        while True:
            current_i += 1
            expected_eid += 1

            given_eid = self._list_entries[current_i].eid

            # update max seen eid
            self._eid_max_seen = max(self._eid_max_seen, given_eid)

            # check if eid is missing
            if given_eid != expected_eid:
                trainable = False

                # set as missing by increasing the missing counter
                if given_eid in self._entry_missing_attempts.keys():
                    Log.mdebug(SarsaQTable._MODULE_NAME, f"_check_trainable_episode: "
                                                         f"missing given_eid={given_eid} "
                                                         f"expected_id={expected_eid}")

                    self._entry_missing_attempts[given_eid] += 1

                    # check if we hit the maximum limit of attempts
                    if self._entry_missing_attempts[given_eid] >= self._entry_missing_max_attempts:
                        Log.mdebug(SarsaQTable._MODULE_NAME, f"_check_trainable_episode: max hit reached #{given_eid}")
                        # reset the list to the next job
                        for i in range(0, current_i):
                            self._list_entries.pop(0)
                            self._lock_empty.release()

                        # restart from that job
                        starting_eid = self._list_entries[0].eid
                        expected_eid = starting_eid
                        current_i = 0
                        trainable = True
                else:
                    self._entry_missing_attempts[given_eid] = 1

                return trainable

            if current_i == self._window_size - 1:
                break

        Log.mdebug(SarsaQTable._MODULE_NAME, f"_check_trainable_episode: episode is trainable={trainable}")
        return trainable

    def _train_window(self):
        """Trigger the window size items"""
        Log.mdebug(SarsaQTable._MODULE_NAME, "_train_window: starting train")

        entry = self._get_train_entry()
        state = entry.state
        action = entry.action
        reward = entry.reward

        self._counter_trained_items += 1

        for i in range(0, self._window_size - 1):
            next_entry = self._get_train_entry()
            next_state = next_entry.state
            next_action = next_entry.action
            next_reward = next_entry.reward

            # train_state = state + [action]
            # next_train_state = state + [next_action]

            # compute the delta
            delta = self._td_form.delta(state, action, next_state, next_action, reward)
            # update the weights
            self._value_function.train(state, action, delta)

            Log.mdebug(SarsaQTable._MODULE_NAME, f"_train_window: trained entry #{i}: eid={next_entry.eid} d={delta}")

            state = next_state
            action = next_action
            reward = next_reward

            self._counter_trained_items += 1
            self._eid_latest_trained = next_entry.eid

        self._counter_episodes += 1

    def _get_train_entry(self) -> LearningEntry:
        entry = self._list_entries.pop(0)
        self._lock_empty.release()
        return entry

    #
    # Utils
    #

    def _check_if_eid_in_list(self, eid) -> bool:
        for entry in self._list_entries:
            if entry.eid == eid:
                return True
        return False

    def _print_entries_list(self):
        for i, entry in enumerate(self._list_entries):
            Log.mdebug(SarsaQTable._MODULE_NAME, f"entry #{i}: {entry}")
