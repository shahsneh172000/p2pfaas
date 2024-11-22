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

#
# Benchmark N machines by using the single machine script
#

import getopt
import json
import math
import mimetypes
import os
import sys
import time
from pathlib import Path
from threading import Thread
from time import localtime, strftime

import requests

from common import CC, ResultsManager, TestManagement, UtilsHttp
from common import read_binary

SCRIPT_NAME = os.path.splitext(os.path.basename(__file__))[0]

# r_mean_time = r"mean_time is [0-9 ^\.]*\.[0-9]*"
# r_pb = r"pB is [0-9 ^\.]*\.[0-9]*"
CHECK_STR = " " + CC.WARNING + "CHCK" + CC.ENDC + " "
OK_STR = "  " + CC.OKGREEN + "OK" + CC.ENDC + "  "
DEAD_STR = " " + CC.FAIL + "DEAD" + CC.ENDC + " "
MISM_STR = " " + CC.WARNING + "MISM" + CC.ENDC + " "
WARN_STR = " " + CC.WARNING + "WARN" + CC.ENDC + " "

BENCHMARK_SCRIPT = "python bench_single_machine.py"
SLEEP_SEC_BETWEEN_TESTS = 10

API_MONITORING_LOAD_URL = "monitoring/load"
RES_API_MONITORING_LOAD_SCHEDULER_NAME = "scheduler_name"
RES_API_MONITORING_LOAD_K = "functions_running_max"

API_DISCOVERY_PORT = 19000
API_DISCOVERY_LIST_URL = "list"


def get_txt_out_full_path(num_thread, l, dir_path):
    return "{0}/lambda{1}-machine-{2:02}.txt".format(dir_path, str(round(l, 2)).replace(".", "_"), num_thread)


def get_res_txt_out_full_path(num_thread, dir_path):
    return "{0}/results-machine-{1:02}.txt".format(dir_path, num_thread)


def do_benchmark(requests_rate=1.0, hosts=None, function_url="", port=80, payloads_dir="", payload_name="",
                 benchmark_time=5 * 60, poisson=True, results_manager=None, learning=False, requests_rate_array=None,
                 learning_reward_deadline=None):
    """Execute the benchmark for each node creating a new thread for every node"""

    print(f"[START] Starting test suite with l = {requests_rate:.2f} l_arr={requests_rate_array}")
    threads = []

    # check the requests rate array
    if requests_rate_array is not None and len(requests_rate_array) != len(hosts):
        print("[START] Requests rate array len is different from the number of hosts")
        return

    # parse the payload
    payload_fullpath = f"{payloads_dir}/{payload_name}"
    payload_bin = read_binary(payload_fullpath)
    payload_mime = mimetypes.guess_type(payload_fullpath)[0]

    def threaded_fun(node_i, node_host_ip, node_request_rate, node_total_requests):
        final_url = f"http://{node_host_ip}:{port}/{function_url}"
        TestManagement.execute_test(node_i,
                                    node_host_ip,
                                    final_url,
                                    payload_name,
                                    payload_bin,
                                    payload_mime,
                                    60,
                                    poisson,
                                    node_total_requests,
                                    node_request_rate,
                                    results_manager,
                                    learning=learning,
                                    learning_reward_fn=TestManagement.learning_reward_fn_latency_custom(
                                        learning_reward_deadline)
                                    )

    for i, host in enumerate(hosts):
        # check the request rate
        request_rate_for_node = requests_rate
        if requests_rate_array is not None:
            request_rate_for_node = requests_rate_array[i]

        # compute the total requests
        total_requests_for_node = int(math.ceil(benchmark_time * request_rate_for_node))

        threads.append(Thread(target=threaded_fun, args=(i, host, request_rate_for_node, total_requests_for_node)))

    # start threads
    for i in range(len(hosts)):
        threads[i].start()
    # wait threads
    for i in range(len(hosts)):
        threads[i].join()

    print("[END] Ending test suite with l = %.2f" % requests_rate)
    print()


def start_suite(hosts, function_url, port, payloads_dir, payloads_list, poisson, start_lambda,
                end_lambda, lambda_delta, dir_log, test_id, learning, requests_rate_array=None, benchmark_time=5 * 60,
                learning_reward_deadline=None):
    results_manager = ResultsManager(f"{dir_log}/{test_id}.db")

    # loop over all payloads
    for payload_name in payloads_list:
        payload_fullpath = f"{payloads_dir}/{payload_name}"
        print(f"==> Starting tests with payload {payload_fullpath}")

        requests_rate = start_lambda

        # loop over all lambda
        while True:
            print(f"==> Starting tests with lambda {requests_rate}, end_lambda {end_lambda}")
            do_benchmark(requests_rate=requests_rate,
                         hosts=hosts,
                         function_url=function_url,
                         port=port,
                         payloads_dir=payloads_dir,
                         payload_name=payload_name,
                         poisson=poisson,
                         results_manager=results_manager,
                         learning=learning,
                         learning_reward_deadline=learning_reward_deadline,
                         requests_rate_array=requests_rate_array,
                         benchmark_time=benchmark_time,
                         )

            # if using a request rate array, only test one lambda, the one in the list
            if requests_rate_array is not None:
                break

            requests_rate = round(requests_rate + lambda_delta, 2)
            if requests_rate > end_lambda:
                break

            # wait some time
            print("\n[SLEEP] Waiting %d secs\n" % SLEEP_SEC_BETWEEN_TESTS)
            time.sleep(SLEEP_SEC_BETWEEN_TESTS)

    results_manager.done()


#
# Checks
#

def check_hosts(hosts, scheduler_port):
    print("==> Checking hosts configurations if matches")
    last_scheduler = ""
    last_k = ""
    test_passed = True

    i = 0
    for host in hosts:
        config_url = "http://{0}:{1}/{2}".format(host, scheduler_port, API_MONITORING_LOAD_URL)
        print("\r[%s] %s checking..." % (CHECK_STR, host), end="")

        ok = True

        try:
            res = requests.get(config_url, timeout=5)
        except (requests.Timeout, requests.ConnectionError) as e:
            print("\r[%s] %s is not responding" % (DEAD_STR, host))
            ok = False
            test_passed = False

        if ok:
            body = res.json()
            this_scheduler = body[RES_API_MONITORING_LOAD_SCHEDULER_NAME]
            this_k = body[RES_API_MONITORING_LOAD_K]
            print_str = OK_STR

            if i == 0:
                last_scheduler = this_scheduler
                last_k = this_k
            elif this_scheduler != last_scheduler or this_k != last_k:
                print_str = MISM_STR
                test_passed = False

            print("\r[%s] %s uses scheduler \"%s\" with k=%d" % (print_str, host, this_scheduler, this_k))

        i += 1

    print()
    return test_passed


def check_discovery_lists(hosts, discovery_port):
    print("==> Checking peers hosts configurations if matches")
    last_hosts = []
    test_passed = True

    def parsePeersArray(peers):
        out = []
        for peer in peers:
            out.append(peer["ip"])
        return out

    i = 0
    for host in hosts:
        config_url = "http://{0}:{1}/{2}".format(host, discovery_port, API_DISCOVERY_LIST_URL)
        print("\r[%s] %s checking..." % (CHECK_STR, host), end="")

        ok = True

        try:
            res = requests.get(config_url, timeout=5)
        except (requests.Timeout, requests.ConnectionError) as e:
            print("\r[%s] %s is not responding" % (DEAD_STR, host))
            ok = False
            test_passed = False

        if ok:
            body = res.json()
            this_hosts = parsePeersArray(body)

            print_str = OK_STR

            if i == 0:
                last_hosts = this_hosts

            if len(this_hosts) == 0:
                print_str = DEAD_STR
                test_passed = False

            if not len(last_hosts) == len(this_hosts):
                print_str = MISM_STR
                test_passed = False

            print("\r[%s] %s knows %d peers" % (print_str, host, len(this_hosts)))

        i += 1

    print()
    return test_passed


def check_function(hosts, scheduler_port, function_url, payload):
    print("==> Checking if function works on all hosts")
    test_passed = True
    payload_binary = None
    payload_mime = None

    if len(payload) > 0:
        payload_binary = read_binary(payload)
        payload_mime = mimetypes.guess_type(payload)[0]

    i = 0
    for host in hosts:
        url = "http://{0}:{1}/{2}".format(host, scheduler_port, function_url)
        print("\r[%s] %s checking function..." % (CHECK_STR, host), end="")

        ok = True

        try:
            headers = {
                'Content-Type': payload_mime,
                'X-P2pfaas-Scheduler-Bypass': "true",
            }
            res = requests.post(url, timeout=5, data=payload_binary, headers=headers)
        except (requests.Timeout, requests.ConnectionError) as e:
            print("\r[%s] %s is not responding" % (DEAD_STR, host))
            ok = False
            test_passed = False

        if ok:
            print_str = OK_STR
            if res.status_code != 200:
                print_str = WARN_STR
                test_passed = False

            print("\r[%s] %s function results is %s" % (print_str, host, res.status_code))

        i += 1

    print()
    return test_passed


def check_payloads(payloads_dir, payload_list):
    print("==> Checking payloads if exist")

    for payload_filename in payload_list:
        payload_full_path = f"{payloads_dir}/{payload_filename}"
        file_exists = os.path.exists(payload_full_path)

        if file_exists:
            print("\r[%s] payload at %s exists" % (OK_STR, payload_full_path))
        else:
            print("\r[%s] payload at %s does not exist" % (DEAD_STR, payload_full_path))
            return False

    print()
    return True


def main(argv):
    hosts_file_path = ""
    scheduler_port = 18080
    discovery_port = 19000
    # requests_n = 200
    poisson = False
    function_url = ""
    start_lambda = 1.0
    end_lambda = 1.1
    lambda_delta = 0.1
    skip_check = False
    test_id = "0"
    payloads_dir = ""
    payloads_list = []
    requests_rate_array = None
    benchmark_time = 5 * 60  # seconds
    learning = False
    learning_reward_deadline = None  # reward if total job time < deadline
    dir_log = "./log"
    # out_dir = ""

    usage = "bench_multi_machine.py"
    try:
        opts, args = getopt.getopt(
            argv, "hf:k:l",
            ["hosts-file=", "function-url=", "requests=", "payload=", "poisson", "start-lambda=", "end-lambda=",
             "lambda-delta=", "scheduler-port=", "discovery-port=", "skip-check", "payloads-dir=",
             "payloads-list=", "requests-rate-array=", "benchmark-time=", "learning", "learning-reward-deadline=",
             "dir-log="])
    except getopt.GetoptError:
        print(usage)
        sys.exit(2)
    for opt, arg in opts:
        # print(opt + " -> " + arg)
        if opt == '-h':
            print(usage)
            sys.exit()
        elif opt in ("-f", "--hosts-file"):
            hosts_file_path = arg
        elif opt in "--scheduler-port":
            scheduler_port = int(arg)
        elif opt in "--discovery-port":
            discovery_port = int(arg)
        elif opt in "--poisson":
            poisson = True
        elif opt in ("-l", "--learning"):
            learning = True
        elif opt in "--function-url":
            function_url = arg
        elif opt in ("-q", "--lambda-delta"):
            lambda_delta = float(arg)
        elif opt in "--start-lambda":
            start_lambda = float(arg)
        elif opt in "--end-lambda":
            end_lambda = float(arg)
        elif opt in "--skip-check":
            skip_check = True
        elif opt in "--payloads-dir":
            payloads_dir = arg
        elif opt in "--payloads-list":
            payloads_list = arg.split(",")
        elif opt in "--requests-rate-array":
            requests_rate_array = list(map(lambda item: round(float(item), 2), arg.split(",")))
        elif opt in "--benchmark-time":
            benchmark_time = int(arg)
        elif opt in "--learning-reward-deadline":
            learning_reward_deadline = float(arg)

    my_file = Path(hosts_file_path)
    if not my_file.is_file():
        print("Passed file does not exist at %s" % hosts_file_path)
        print(usage)
        sys.exit()

    # if out_dir == "":
    time_str = strftime("%m%d%Y-%H%M%S", localtime())
    # out_dir = "./_{}-{}".format(SCRIPT_NAME, time_str)
    test_id = time_str

    hosts_file_f = open(hosts_file_path, "r")
    hosts = []
    for line in hosts_file_f:
        # skip commented lines
        if line[0] == "#":
            continue
        hosts.append(line.strip())
    hosts_file_f.close()

    specification_str = f'''
====== P2P-FOG Multi-Machine benchmark ======
> test_id {test_id}
> hosts_file_path {hosts_file_path}
> scheduler_port {scheduler_port}
> discovery_port {discovery_port}
> hosts {hosts}
> function_url {function_url}
> poisson {poisson}
> lambda [{start_lambda:.2f}, {end_lambda:.2f}]
> lambda_delta {lambda_delta:.2f}
> skip_check {skip_check}
> dir_log {dir_log}
> payloads_dir {payloads_dir}
> payloads_list {payloads_list}
> requests_rate_array {requests_rate_array}
> benchmark_time {benchmark_time}
> learning {learning}
> learning_reward_deadline {learning_reward_deadline}
'''

    print(specification_str)
    # save to file
    spec_fp = f"{dir_log}/{test_id}.txt"
    spec_file = open(spec_fp, "w")
    print(specification_str, file=spec_file)
    spec_file.close()

    if len(hosts) == 0:
        print("No host passed!")
        sys.exit(1)

    if not skip_check:
        # if not checkHosts(hosts, scheduler_port):
        #     print("Preliminary hosts check not passed!")
        #     sys.exit(1)

        if not check_payloads(payloads_dir, payloads_list):
            print("Preliminary payloads check not passed!")
            sys.exit(1)

        if not check_discovery_lists(hosts, discovery_port):
            print("Preliminary discovery check not passed!")
            sys.exit(1)

        if not check_function(hosts, scheduler_port, function_url, f"{payloads_dir}/{payloads_list[0]}"):
            print("Preliminary function check not passed!")
            sys.exit(1)

        if not UtilsHttp.check_same_http_response("Scheduler params", hosts, 18080, "configuration/scheduler", spec_fp):
            print("Preliminary function check not passed!")
            sys.exit(1)

        if learning:
            if not UtilsHttp.check_same_http_response("Learning params", hosts, 19020, "learner/parameters", spec_fp):
                print("Preliminary function check not passed!")
                sys.exit(1)
            # if not check_same_http_response("Learning stats", hosts, 19020, "learner/stats"):
            #     print("Preliminary function check not passed!")
            #     sys.exit(1)

    os.makedirs(dir_log, exist_ok=True)

    start_suite(hosts,
                function_url,
                scheduler_port,
                payloads_dir,
                payloads_list,
                poisson,
                start_lambda,
                end_lambda,
                lambda_delta,
                dir_log,
                test_id,
                learning,
                requests_rate_array=requests_rate_array,
                benchmark_time=benchmark_time,
                learning_reward_deadline=learning_reward_deadline,
                )

    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1:])
