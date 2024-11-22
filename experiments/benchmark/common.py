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
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
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
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
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
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
import json
import random
import sqlite3
import time
from dataclasses import dataclass
from threading import Thread, Lock
from typing import List, Callable

import requests

import log
from log import Log


class CC:
    """Class which holds terminal colors"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def read_binary(uri):
    if uri == "" or uri is None:
        return None

    in_file = open(uri, "rb")  # opening for [r]eading as [b]inary
    data = in_file.read()  # if you only wanted to read 512 bytes, do .read(512)
    in_file.close()

    return data


#
# Test management
#

@dataclass(init=False)
class TestExecutionResults:
    req_id: int
    node_id: int
    requests_rate: float
    payload_name: str

    timestamp_start: float
    timestamp_end: float

    time_total: float
    time_execution: float

    times_probing: List[float]
    times_scheduling: List[float]
    times_service: List[float]

    times_parsed: bool

    did_probing: bool
    status_code: int
    net_error: bool
    externally_executed: bool
    hops: int

    l_eid: int
    l_state: List[float]
    l_action: float
    l_eps: float
    l_reward: float
    l_parsed: bool

    def __init__(self):
        self.node_id = 0
        self.req_id = 0
        self.requests_rate = 0.0
        self.payload_name = ""

        self.timestamp_start = 0.0
        self.timestamp_end = 0.0

        self.time_total = 0.0
        self.time_execution = 0.0

        self.times_probing = []
        self.times_scheduling = []
        self.times_service = []

        self.times_parsed = False

        self.status_code = -1
        self.net_error = False
        self.externally_executed = False
        self.hops = 0

        # learning
        self.l_eid = 0
        self.l_state = []
        self.l_action = 0.0
        self.l_eps = 0.0
        self.l_reward = 0.0
        self.l_parsed = False


_MODULE_NAME = "TestManagement"


class TestManagement:
    DEBUG = False

    RES_HEADER_EXTERNALLY_EXECUTED = "X-P2pfaas-Externally-Executed"
    RES_HEADER_HOPS = "X-P2pfaas-Hops"

    RES_HEADER_EXECUTION_TIME = "X-P2pfaas-Timing-Execution-Time-Seconds"
    RES_HEADER_TOTAL_TIME = "X-P2pfaas-Timing-Total-Time-Seconds"
    RES_HEADER_SCHEDULING_TIME = "X-P2pfaas-Timing-Scheduling-Time-Seconds"
    RES_HEADER_PROBING_TIME = "X-P2pfaas-Timing-Probing-Time-Seconds"

    RES_HEADER_SCHEDULING_TIME_LIST = "X-P2pfaas-Timing-Scheduling-Seconds-List"
    RES_HEADER_TOTAL_TIME_LIST = "X-P2pfaas-Timing-Total-Seconds-List"
    RES_HEADER_PROBING_TIME_LIST = "X-P2pfaas-Timing-Probing-Seconds-List"

    RES_HEADER_SCHEDULER_LEARNING_EID = "X-P2pfaas-Scheduler-Learning-Eid"
    RES_HEADER_SCHEDULER_LEARNING_STATE = "X-P2pfaas-Scheduler-Learning-State"
    RES_HEADER_SCHEDULER_LEARNING_ACTION = "X-P2pfaas-Scheduler-Learning-Action"
    RES_HEADER_SCHEDULER_LEARNING_EPS = "X-P2pfaas-Scheduler-Learning-Eps"

    HEADER_LEARNING_EID = "X-P2pfaas-Learning-Eid"
    HEADER_LEARNING_STATE = "X-P2pfaas-Learning-State"
    HEADER_LEARNING_ACTION = "X-P2pfaas-Learning-Action"
    HEADER_LEARNING_REWARD = "X-P2pfaas-Learning-Reward"

    STACK_LEARNER_PORT = 19020

    @staticmethod
    def execute_test(node_id, node_host, url, payload_name, payload_bin, payload_mime, timeout, poisson=True,
                     total_requests=1000, requests_rate=1.0, results_manager=None,
                     learning=False, learning_reward_fn=lambda _: 1.0):
        """ Execute test by passing ro and mi as average execution time """
        threads = []  # keep last 100

        # session_benchmark = requests.Session()
        # session_learning = requests.Session()

        # reset if needed
        if learning:
            log.Log.mdebug(_MODULE_NAME, f"[TEST] (Node{node_id}) Resetting the learner...")
            TestManagement._learning_reset(node_host)

        # request loop
        log.Log.mdebug(_MODULE_NAME, f"[TEST] (Node{node_id} {node_host}) Started test, "
                                     f"l={requests_rate} reqs={total_requests}")
        for req_id in range(total_requests):
            started_request_time = time.time()

            # log.Log.mdebug(_MODULE_NAME, f"[TEST] (Node{node_id}) Request {req_id + 1}/{total_requests} url={url}")

            thread = Thread(target=TestManagement._get_request,
                            args=(node_id, node_host, url, payload_name, payload_bin, payload_mime, timeout,
                                  req_id, requests_rate, results_manager, learning, learning_reward_fn))

            # add thread to list
            if len(threads) > 100:
                threads.pop(0)
            threads.append(thread)

            thread.start()

            # compute time to wait
            wait_for = 0.0
            if poisson:
                wait_for = random.expovariate(requests_rate)

            # check if wait time elapsed
            elapsed = time.time() - started_request_time
            if elapsed < wait_for:
                time.sleep(wait_for - elapsed)

        for t in threads:
            t.join()

    @staticmethod
    def _get_request(node_id, node_host, url, payload_name, payload_bin, payload_mime, timeout, req_id, requests_rate,
                     results_manager, learning, learning_reward_fn):
        # if node_id == 0:
        # log.Log.mdebug(_MODULE_NAME, f"[TEST] get_request node_id={node_id} req_id={req_id} url={url}")

        test_results = TestExecutionResults()
        test_results.node_id = node_id
        test_results.requests_rate = requests_rate
        test_results.payload_name = payload_name

        res = None

        test_results.node_id = node_id
        test_results.req_id = req_id
        test_results.timestamp_start = time.time()
        start_time = time.time()

        try:
            headers = {'Content-Type': payload_mime}
            res = requests.post(url, data=payload_bin, headers=headers, timeout=timeout)

        except Exception as e:
            Log.merr(_MODULE_NAME, f"RequestError: id={req_id}, url={url}, e={e}")
            test_results.net_error = True
            # end_time = time.time()
            # total_time = end_time - start_time
            # print(f"Total time {total_time / 1000}")

        end_time = time.time()
        total_time = end_time - start_time
        test_results.timestamp_end = time.time()
        test_results.time_total = total_time

        # if net error we log the error but training cannot be done
        if test_results.net_error or res is None:
            if results_manager is not None:
                results_manager.log_job_end(test_results)
            else:
                print("Results manager is None, not saving results")
            return

        # update result
        test_results.status_code = res.status_code
        test_results.externally_executed = res.headers.get(TestManagement.RES_HEADER_EXTERNALLY_EXECUTED) is not None

        hops_header = res.headers.get(TestManagement.RES_HEADER_HOPS)
        test_results.hops = 0 if hops_header is None else int(hops_header)

        # parse timing headers if request is successful
        if res.status_code == 200:
            TestManagement._parse_timings_headers(res.headers, test_results)

        # compute the reward in any case
        if learning_reward_fn is not None:
            test_results.l_reward = learning_reward_fn(test_results)

        # start learning phase
        if learning:
            # retrieve state, action and eps
            TestManagement._parse_learning_headers(res.headers, test_results)
            # log the entry to the stack-learner in a separate thread
            Thread(target=TestManagement._learning_log_entry, args=(node_host, test_results)).start()

        if results_manager is not None:
            results_manager.log_job_end(test_results)
        else:
            print("Results manager is None, not saving results")

    @staticmethod
    def _parse_timings_headers(headers, test_results: TestExecutionResults):
        if headers is None:
            return

        try:
            total_time_header = headers.get(TestManagement.RES_HEADER_TOTAL_TIME_LIST)
            scheduling_time_header = headers.get(TestManagement.RES_HEADER_SCHEDULING_TIME_LIST)
            probing_time_header = headers.get(TestManagement.RES_HEADER_PROBING_TIME_LIST)
            execution_time_header = headers.get(TestManagement.RES_HEADER_EXECUTION_TIME)

            if total_time_header is not None:
                total_times_array = json.loads(total_time_header)
                test_results.times_service = total_times_array

            if scheduling_time_header is not None:
                scheduling_time_array = json.loads(scheduling_time_header)
                test_results.times_scheduling = scheduling_time_array

            if probing_time_header is not None:
                probing_time_array = json.loads(probing_time_header)
                test_results.times_probing = probing_time_array

            if execution_time_header is not None:
                test_results.time_execution = float(execution_time_header)

            test_results.times_parsed = True

        except Exception as e:
            print(f"{CC.FAIL}==> [ERR] Cannot parse timing for req: {e}{CC.ENDC}")
            print(f"{CC.FAIL}==> [ERR] Cannot parse timing for req: {headers}{CC.ENDC}")

    @staticmethod
    def _parse_learning_headers(headers, test_results: TestExecutionResults):
        if headers is None:
            return

        try:
            state_header = headers.get(TestManagement.RES_HEADER_SCHEDULER_LEARNING_STATE)
            action_header = headers.get(TestManagement.RES_HEADER_SCHEDULER_LEARNING_ACTION)
            eps_header = headers.get(TestManagement.RES_HEADER_SCHEDULER_LEARNING_EPS)
            eid_header = headers.get(TestManagement.RES_HEADER_SCHEDULER_LEARNING_EID)

            if state_header is not None:
                test_results.l_state = state_header
            if action_header is not None:
                test_results.l_action = float(action_header)
            if eps_header is not None:
                test_results.l_eps = float(eps_header)
            if eid_header is not None:
                test_results.l_eid = int(eid_header)

            test_results.l_parsed = True

        except Exception as e:
            print(f"{CC.FAIL}==> [ERR] Cannot parse timing for req: {e}{CC.ENDC}")
            print(f"{CC.FAIL}==> [ERR] Cannot parse timing for req: {headers}{CC.ENDC}")

    #
    # Learning
    #

    @staticmethod
    def learning_reward_fn_default(results: TestExecutionResults) -> float:
        if results.status_code == 200:
            return 1.0
        return 0.0

    @staticmethod
    def learning_reward_fn_latency(results: TestExecutionResults) -> float:
        if results.time_total <= 0.220:
            return 1.0
        return 0.0

    @staticmethod
    def learning_reward_fn_latency_custom(deadline: float) -> Callable[[TestExecutionResults], float]:
        if deadline is None:
            return TestManagement.learning_reward_fn_latency

        def reward_fn(results: TestExecutionResults):
            if results.status_code == 200 and results.time_total <= deadline:
                return 1.0
            return 0.0

        return reward_fn

    @staticmethod
    def _learning_log_entry(node_host, result: TestExecutionResults):
        """Log the LearningEntry to the stack-learner component of P2PFaaS"""

        if False and node_host == "192.168.50.100":
            Log.mdebug(_MODULE_NAME, f"Logging learning entry: "
                                     f"eid={result.l_eid} "
                                     f"state={result.l_state} "
                                     f"action={result.l_action} "
                                     f"reward={result.l_reward} "
                                     f"total_time={result.time_total:.3f}")
        try:
            headers = {
                TestManagement.HEADER_LEARNING_EID: f"{result.l_eid}",
                TestManagement.HEADER_LEARNING_STATE: result.l_state,
                TestManagement.HEADER_LEARNING_ACTION: f"{result.l_action:.4f}",
                TestManagement.HEADER_LEARNING_REWARD: f"{result.l_reward:.4f}",
            }
            # log.Log.mdebug(_MODULE_NAME, f"[TEST] ({node_host}) Logging learning entry with headers {headers}")

            res = requests.get(f"http://{node_host}:{TestManagement.STACK_LEARNER_PORT}/train",
                               headers=headers,
                               timeout=30)
            if res.status_code != 200:
                print(f"{CC.FAIL}==> [ERR] Cannot log learning entry: statusCode={res.status_code}{CC.ENDC}")

        except Exception as e:
            print(f"{CC.FAIL}==> [ERR] Cannot log learning entry: {e}{CC.ENDC}")

    @staticmethod
    def _learning_reset(node_host):
        """Reset the state of the stack-learner component of P2PFaaS"""
        try:
            res = requests.get(f"http://{node_host}:{TestManagement.STACK_LEARNER_PORT}/learner/reset", timeout=30)
            if res.status_code != 200:
                print(f"{CC.FAIL}==> [ERR] Cannot log learning entry: statusCode={res.status_code}{CC.ENDC}")

        except Exception as e:
            print(f"{CC.FAIL}==> [ERR] Cannot log learning entry: {e}{CC.ENDC}")


#
# Results DB management
#

class ResultsManager:
    TIME_TYPE_SCHEDULING = "scheduling"
    TIME_TYPE_SERVICE = "service"
    TIME_TYPE_PROBING = "probing"

    def __init__(self, filepath):
        self._filepath = filepath

        self._db = sqlite3.connect(':memory:', check_same_thread=False)
        self._db_cur = self._db.cursor()

        self._init_db()

        self.mutex = Lock()

    #
    # Exported
    #

    def log_job_end(self, results: TestExecutionResults):
        self.mutex.acquire()

        # if results.node_id == 0:
        #     print(f"[TEST] db get_request node_id={results.node_id} req_id={results.req_id:4d}")

        self._db_cur.execute(f'''INSERT INTO jobs VALUES (
                                        {results.node_id},
                                        {results.req_id},
                                        "{results.payload_name}",
                                        {results.requests_rate},
                                        {results.time_total},
                                        {results.time_execution},
                                        {1 if results.times_parsed else 0},
                                        {results.status_code},
                                        {1 if results.net_error else 0},
                                        {1 if results.externally_executed else 0},
                                        {results.timestamp_start},
                                        {results.timestamp_end},
                                        {results.l_eps},
                                        {results.l_reward}
                            )''')

        for i, value in enumerate(results.times_probing):
            self._log_timing(results.node_id, results.req_id, results.payload_name, results.requests_rate, i,
                             ResultsManager.TIME_TYPE_PROBING, value)
        for i, value in enumerate(results.times_service):
            self._log_timing(results.node_id, results.req_id, results.payload_name, results.requests_rate, i,
                             ResultsManager.TIME_TYPE_SERVICE, value)
        for i, value in enumerate(results.times_scheduling):
            self._log_timing(results.node_id, results.req_id, results.payload_name, results.requests_rate, i,
                             ResultsManager.TIME_TYPE_SCHEDULING, value)

        self._db.commit()

        self.mutex.release()

    def _log_timing(self, node_id, req_id, payload_name, requests_rate, index, time_type, time_value):
        self._db_cur.execute(f'''INSERT INTO timings VALUES (
                                        {node_id},
                                        {req_id},
                                        "{payload_name}",
                                        {requests_rate},
                                        {index},
                                        "{time_type}",
                                        {time_value}
        )''')

    def done(self):
        self._copy_db_to_file()
        self._db.close()

    #
    # Internals
    #

    def _init_db(self):
        self._db_cur.execute('''
        CREATE TABLE jobs (
                                                     node_id integer, 
                                                     req_id integer, 
                                                     payload_name text, 
                                                     requests_rate real,
                                                     time_total real, 
                                                     time_execution real, 
                                                     times_parsed integer, 
                                                     status_code integer,
                                                     net_error integer,
                                                     externally_executed integer,
                                                     timestamp_start real,
                                                     timestamp_end real,
                                                     learning_eps real,
                                                     learning_reward real
                                                 )
                                                 ''')

        self._db_cur.execute('''CREATE TABLE timings (
                                                     node_id integer, 
                                                     req_id integer, 
                                                     payload_name text,
                                                     requests_rate real,
                                                     index_i integer,
                                                     time_type text, 
                                                     time_value real
                                                 )''')

    def _copy_db_to_file(self):
        print("Copying memory db to file, please wait")

        start = time.time()

        new_db = sqlite3.connect(self._filepath)
        query = "".join(line for line in self._db.iterdump())

        # Dump old database in the new one.
        new_db.executescript(query)
        new_db.close()

        print(f"Done in {time.time() - start:2f}")


#
# Logging
#

class UtilsLog:
    CHECK_STR = " " + CC.WARNING + "CHCK" + CC.ENDC + " "
    OK_STR = "  " + CC.OKGREEN + "OK" + CC.ENDC + "  "
    DEAD_STR = " " + CC.FAIL + "DEAD" + CC.ENDC + " "
    MISM_STR = " " + CC.WARNING + "MISM" + CC.ENDC + " "
    WARN_STR = " " + CC.WARNING + "WARN" + CC.ENDC + " "


#
# Http utils
#

class UtilsHttp:

    @staticmethod
    def check_same_http_response(name, hosts, port, url, append_to_filepath=None):
        print(f"==> Checking {name}")
        last_result_str = ""
        last_result_code = 200
        test_passed = True
        res = None

        i = 0
        for host in hosts:
            final_url = f"http://{host}:{port}/{url}"
            print(f"\r[{UtilsLog.CHECK_STR}] {host} checking at {final_url}...", end="")

            ok = True

            try:
                res = requests.get(final_url, timeout=5)
            except (requests.Timeout, requests.ConnectionError) as e:
                print("\r[%s] %s is not responding" % (UtilsLog.DEAD_STR, host))
                ok = False
                test_passed = False

            if ok and res is not None:
                body_str = json.dumps(res.json())
                res_code = res.status_code

                print_str = UtilsLog.OK_STR

                if i == 0:
                    last_result_str = body_str
                    last_result_code = res_code
                elif last_result_str != body_str or last_result_code != res_code:
                    print_str = UtilsLog.MISM_STR
                    test_passed = False

                print(f"\r[{print_str}] {host} replied with {body_str}")

            i += 1

        print()

        if append_to_filepath is not None:
            metafile = open(append_to_filepath, "a")
            print(f"==> Payload for check={name}", file=metafile)
            print(last_result_str, file=metafile)
            print("", file=metafile)

        return test_passed
