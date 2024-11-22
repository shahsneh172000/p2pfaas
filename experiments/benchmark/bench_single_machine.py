#  P2PFaaS - A framework for FaaS Load Balancing
#  Copyright (c) 2019 - 2022. Gabriele Proietti Mattia <pm.gabriele@outlook.com>
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
# This script benchmarks a single machine by sending requests in parallel.
#

import getopt
import json
import mimetypes
import os
import random
import sys
import time
from threading import Thread
from time import localtime, strftime

import requests

from common import CC
from common import read_binary

SCRIPT_NAME = os.path.splitext(os.path.basename(__file__))[0]

RES_API_MONITORING_LOAD_SCHEDULER_NAME = "scheduler_name"
RES_API_MONITORING_LOAD_K = "functions_running_max"

API_MONITORING_LOAD_URL = "monitoring/load"
API_SCHEDULER_CONFIGURATION_URL = "configuration/scheduler"
API_CONFIGURATION_URL = "configuration"
API_HELLO_URL = ""

RES_SCHEDULER_CONFIGURATION_NAME = "name"
RES_SCHEDULER_CONFIGURATION_PARAMETERS = "parameters"

RES_CONFIGURATION_RUNNING_FUNCTIONS_MAX = "running_functions_max"

RES_HELLO_VERSION = "version"

TIMEOUT = 120

# features
FEATURE_LAMBDA = "lambda"
FEATURE_PB = "pb"
FEATURE_PE = "pe"
FEATURE_NET_ERRORS = "net_errors"
TIMING_TOTAL_TIME = "total_time"  # total time for the request to be completed from client
TIMING_TOTAL_SRV_TIME = "total_srv_time"  # total time for the request to be completed when arrived to server
TIMING_SCHEDULING_TIME = "scheduling_time"  # time between a job arrives and it is decided where it should be executed
TIMING_EXECUTION_TIME = "execution_time"  # pure time for executing a job
TIMING_PROBING_TIME = "probing_time"  # total time for the request to be completed
TIMING_FORWARDING_TIME = "forwarding_time"  # total time for the job to be forwarded

# headers
RES_HEADER_EXTERNALLY_EXECUTED = "X-P2pfaas-Externally-Executed"
RES_HEADER_HOPS = "X-P2pfaas-Hops"

RES_HEADER_EXECUTION_TIME = "X-P2pfaas-Timing-Execution-Time-Seconds"
RES_HEADER_TOTAL_TIME = "X-P2pfaas-Timing-Total-Time-Seconds"
RES_HEADER_SCHEDULING_TIME = "X-P2pfaas-Timing-Scheduling-Time-Seconds"
RES_HEADER_PROBING_TIME = "X-P2pfaas-Timing-Probing-Time-Seconds"

RES_HEADER_SCHEDULING_TIME_LIST = "X-P2pfaas-Timing-Scheduling-Seconds-List"
RES_HEADER_TOTAL_TIME_LIST = "X-P2pfaas-Timing-Total-Seconds-List"
RES_HEADER_PROBING_TIME_LIST = "X-P2pfaas-Timing-Probing-Seconds-List"


class FunctionTest:

    def __init__(self, url, payload, l, k, poisson, n_requests, out_dir, machine_id, verbose, debug=False):
        self.debug_print = debug
        self.verbose = verbose
        self.url = url
        self.payload = payload
        self.l = l
        self.k = k
        self.out_dir = out_dir
        self.poisson = poisson
        self.test_name = "k" + str(k) + "_lambda" + str(round(l, 3)).replace(".", "_")
        self.machine_id = machine_id
        self.payload_binary = None
        self.payload_mime = None

        # prepare suite parameters
        self.total_requests = n_requests  # to be updated after test
        self.wait_time = 1 / self.l

        self.threads = []
        self._n_accepted_jobs = 0  # jobs with response code == 200
        self._n_rejected_jobs = 0  # jobs with response code == 500
        self._n_external_jobs = 0  # jobs executed externally
        self._n_external_jobs_accepted = 0  # jobs executed externally and accepted
        self._n_neterr_jobs = 0  # jobs that had a network error
        self._n_probed_jobs = 0  # jobs for which probing has been done

        # final metrics
        self._metric_mean_total_time = 0.0
        self._metric_mean_total_srv_time = 0.0
        self._metric_mean_scheduling_time = 0.0
        self._metric_mean_execution_time = 0.0
        self._metric_mean_probing_time = 0.0
        self._metric_mean_forwarding_time = 0.0
        self._metric_pa = 0.0
        self._metric_pb = 0.0
        self._metric_pe = 0.0

        self.total_probe_messages = 0

        # per-thread variables
        self._timings = {
            TIMING_TOTAL_TIME: [0.0] * self.total_requests,
            TIMING_TOTAL_SRV_TIME: [0.0] * self.total_requests,
            TIMING_EXECUTION_TIME: [0.0] * self.total_requests,
            TIMING_PROBING_TIME: [0.0] * self.total_requests,
            TIMING_SCHEDULING_TIME: [0.0] * self.total_requests,
            TIMING_FORWARDING_TIME: [0.0] * self.total_requests,
        }
        self._req_output = [None] * self.total_requests
        self._req_external = [None] * self.total_requests
        self._req_did_probing = [None] * self.total_requests
        self._req_probe_messages = [0] * self.total_requests

        print("[INIT] Starting test")

        # load payload
        if len(payload) > 0:
            self.payload_binary = read_binary(self.payload)
            self.payload_mime = mimetypes.guess_type(self.payload)[0]
            print("[INIT] Loaded payload of mime " + self.payload_mime)

    @staticmethod
    def get_features():
        return [FEATURE_LAMBDA, FEATURE_PB, FEATURE_PE, TIMING_TOTAL_TIME, TIMING_TOTAL_SRV_TIME,
                TIMING_SCHEDULING_TIME, TIMING_EXECUTION_TIME, TIMING_PROBING_TIME, TIMING_FORWARDING_TIME,
                FEATURE_NET_ERRORS]

    def execute_test(self):
        """ Execute test by passing ro and mi as average execution time """

        print("[TEST] Starting with l = %.2f, k = %d, Poisson = %s" % (self.l, self.k, self.poisson))

        def get_request(arg: int):
            start_time = time.time()
            net_error = False
            res = None

            if self.debug_print:
                print("==> [GET] Number #" + str(arg))

            try:
                headers = {'Content-Type': self.payload_mime}
                res = requests.post(self.url, data=self.payload_binary, headers=headers, timeout=TIMEOUT)
            except Exception as e:
                print(e)
                net_error = True

            end_time = time.time()
            total_time = end_time - start_time

            # update timings
            self._timings[TIMING_TOTAL_TIME][arg] = total_time

            # check if net error
            if net_error:
                self._req_output[arg] = 999
                return

            self._req_external[arg] = res.headers.get(RES_HEADER_EXTERNALLY_EXECUTED) is not None
            self._req_output[arg] = res.status_code

            # get probed status
            if self._req_external[arg]:
                self._req_did_probing[arg] = res.headers.get(RES_HEADER_PROBING_TIME_LIST) is not None
            else:
                self._req_did_probing[arg] = res.headers.get(RES_HEADER_PROBING_TIME) is not None

            # parse headers if request is successful
            if res.status_code == 200:
                self.parse_timings_headers(res.headers, arg)

            # print debug res line
            self.print_req_res_line(arg, res, net_error, total_time)

        def burst_requests():
            if not self.debug_print:
                print("[TEST] Request %d/%d" % (0, self.total_requests), end='')
            for i in range(self.total_requests):
                print("\r[TEST] Request %d/%d" % (i + 1, self.total_requests), end='')
                thread = Thread(target=get_request, args=(i,))
                thread.start()
                self.threads.append(thread)
                time.sleep(self.wait_time)

            for t in self.threads:
                t.join()

        def poisson_requests():
            elapsed = 0.0
            req_n = 0

            print("\r[TEST] Starting...", end='')
            for i in range(self.total_requests):
                wait_for = random.expovariate(self.l)

                if self.verbose:
                    print("\r[TEST] Request %4d/%4d | Elapsed Sec. %4.2f | Next in %.2fs" % (
                        req_n + 1, self.total_requests, elapsed, wait_for), end='')
                thread = Thread(target=get_request, args=(i,))
                self.threads.append(thread)

                elapsed += wait_for
                req_n += 1

                thread.start()
                time.sleep(wait_for)

            for t in self.threads:
                t.join()

        if self.poisson:
            poisson_requests()
        else:
            burst_requests()

        self.compute_stats()

    def compute_stats(self):
        timings_total_sum = 0.0
        timings_total_srv_sum = 0.0
        timings_execution_sum = 0.0
        timings_scheduling_sum = 0.0
        timings_probing_sum = 0.0
        timings_forwarding_sum = 0.0

        for i in range(len(self._req_output)):
            self.total_probe_messages += self._req_probe_messages[i]
            if self._req_output[i] == 200:
                self._n_accepted_jobs += 1
                timings_total_sum += self._timings[TIMING_TOTAL_TIME][i]
                timings_total_srv_sum += self._timings[TIMING_TOTAL_SRV_TIME][i]
                timings_execution_sum += self._timings[TIMING_EXECUTION_TIME][i]
                timings_scheduling_sum += self._timings[TIMING_SCHEDULING_TIME][i]
                timings_probing_sum += self._timings[TIMING_PROBING_TIME][i]

            elif self._req_output[i] == 500:
                self._n_rejected_jobs += 1
            else:
                self._n_neterr_jobs += 1

            if self._req_external[i]:
                timings_forwarding_sum += self._timings[TIMING_FORWARDING_TIME][i]
                self._n_external_jobs += 1

            if self._req_did_probing[i]:
                self._n_probed_jobs += 1

            if self._req_external[i] and self._req_output[i] == 200:
                self._n_external_jobs_accepted += 1

        self._metric_pb = self._n_rejected_jobs / float(self.total_requests)
        self._metric_pa = self._n_accepted_jobs / float(self.total_requests)
        self._metric_pe = self._n_external_jobs / float(self.total_requests)

        if self._n_accepted_jobs > 0:
            # internal_jobs = self.accepted_jobs - self.external_jobs
            self._metric_mean_total_time = timings_total_sum / float(self._n_accepted_jobs)
            self._metric_mean_total_srv_time = timings_total_srv_sum / float(self._n_accepted_jobs)
            self._metric_mean_execution_time = timings_execution_sum / float(self._n_accepted_jobs)
            self._metric_mean_scheduling_time = timings_scheduling_sum / float(self._n_accepted_jobs)

        if self._n_external_jobs_accepted > 0:
            self._metric_mean_forwarding_time = timings_forwarding_sum / float(self._n_external_jobs)

        if self._n_probed_jobs > 0:
            self._metric_mean_probing_time = timings_probing_sum / float(self._n_probed_jobs)

        print(
            "\n[TEST] Done. Of %d jobs, %d accepted, %d rejected, %d externally executed, %d probed jobs, %d had network error." %
            (self.total_requests, self._n_accepted_jobs, self._n_rejected_jobs, self._n_external_jobs,
             self._n_probed_jobs, self._n_neterr_jobs))
        print("[TEST] pB is %.6f, mean_request_time is %.6f, mean_probing_time is %.6f" % (
            self._metric_pb, self._metric_mean_total_time, self._metric_mean_probing_time))
        print("[TEST] %.6f%% jobs externally executed, forwarding and scheduling times are %.6fs %.6fs\n" % (
            self._metric_pe, self._metric_mean_forwarding_time, self._metric_mean_scheduling_time))

    def save_request_timings(self):
        if self.out_dir == "":
            return
        file_path = "{}/req-times-l{}-machine{:02}.txt".format(self.out_dir,
                                                               str(round(self.l, 3)).replace(".", "_"), self.machine_id)
        f = open(file_path, "w")
        f.write("# mean={} - {} jobs {}/{} (a/r) - l={:.2} - k={}\n".format(self._metric_mean_total_time,
                                                                            self.total_requests,
                                                                            self._n_accepted_jobs,
                                                                            self._n_rejected_jobs,
                                                                            self.l, self.k))
        for i in range(len(self._timings[TIMING_TOTAL_TIME])):
            if self._req_output[i] == 200:
                f.write("{}\n".format(self._timings[TIMING_TOTAL_TIME][i]))
        f.close()

    #
    # Getters
    #

    def get_pb(self):
        return self._metric_pb

    def get_pe(self):
        return self._metric_pe

    def get_probe_messages(self):
        return self.total_probe_messages

    def get_timings(self):
        return {
            TIMING_TOTAL_TIME: self._metric_mean_total_time,
            TIMING_TOTAL_SRV_TIME: self._metric_mean_total_srv_time,
            TIMING_EXECUTION_TIME: self._metric_mean_execution_time,
            TIMING_SCHEDULING_TIME: self._metric_mean_scheduling_time,
            TIMING_PROBING_TIME: self._metric_mean_probing_time,
            TIMING_FORWARDING_TIME: self._metric_mean_forwarding_time,
        }

    def get_net_errors(self):
        return self._n_neterr_jobs

    #
    # Utils
    #

    def print_req_res_line(self, i, res, net_error, time_s):
        if not self.debug_print:
            return

        if not net_error:
            if res.status_code == 200:
                print(
                    "%s ==> [RES] Status to #%d is %d Time %.6f, external=%s, did_probing=%s %s" % (
                        CC.OKGREEN, i, res.status_code, time_s, self._req_external[i], self._req_did_probing[i],
                        CC.ENDC))
            else:
                print(
                    "%s ==> [RES] Status to #%d is %d Time %.6f, external=%s, did_probing=%s %s" % (
                        CC.FAIL, i, res.status_code, time_s, self._req_external[i], self._req_did_probing[i], CC.ENDC))
                print(str(res.content))

    def parse_timings_headers(self, headers, i):
        try:
            # we have arrays of timings if job is externally executed
            if headers.get(RES_HEADER_EXTERNALLY_EXECUTED) is not None:
                total_times_array = json.loads(headers.get(RES_HEADER_TOTAL_TIME_LIST))
                scheduling_time_array = json.loads(headers.get(RES_HEADER_SCHEDULING_TIME_LIST))
                probing_time_array = json.loads(headers.get(RES_HEADER_PROBING_TIME_LIST))

                # if len(total_times_array) == len(scheduling_time_array) == len(probing_time_array):
                #    for i in range(len(total_times_array)):
                probing_time = probing_time_array[0]
                scheduling_time = scheduling_time_array[0]
                total_srv_time = total_times_array[0]

                self._timings[TIMING_FORWARDING_TIME][i] = total_times_array[0] - total_times_array[1]
            else:
                # we have single values
                scheduling_time = 0.0 if headers.get(RES_HEADER_SCHEDULING_TIME) is None else float(
                    headers.get(RES_HEADER_SCHEDULING_TIME))
                probing_time = 0.0 if headers.get(RES_HEADER_PROBING_TIME) is None else float(
                    headers.get(RES_HEADER_PROBING_TIME))
                total_srv_time = 0.0 if headers.get(RES_HEADER_TOTAL_TIME) is None else float(
                    headers.get(RES_HEADER_TOTAL_TIME))

            execution_time = 0.0 if headers.get(RES_HEADER_EXECUTION_TIME) is None else float(
                headers.get(RES_HEADER_EXECUTION_TIME))

            self._timings[TIMING_SCHEDULING_TIME][i] = scheduling_time
            self._timings[TIMING_PROBING_TIME][i] = probing_time
            self._timings[TIMING_TOTAL_SRV_TIME][i] = total_srv_time
            self._timings[TIMING_EXECUTION_TIME][i] = execution_time
        except Exception as e:
            print(f"{CC.FAIL}==> [ERR] Cannot parse timing for req #{i}: {e}{CC.ENDC}")
            print(f"{CC.FAIL}==> [ERR] Cannot parse timing for req #{i}: {headers}{CC.ENDC}")


def get_system_params(host):
    config_url = "http://{0}/{1}".format(host, API_CONFIGURATION_URL)
    config_s_url = "http://{0}/{1}".format(host, API_SCHEDULER_CONFIGURATION_URL)
    config_h_url = "http://{0}/{1}".format(host, API_HELLO_URL)
    res = requests.get(config_url)
    res_s = requests.get(config_s_url)
    res_h = requests.get(config_h_url)
    body = res.json()
    body_s = res_s.json()
    body_h = res_h.json()
    return {
        RES_SCHEDULER_CONFIGURATION_NAME: body_s[RES_SCHEDULER_CONFIGURATION_NAME],
        RES_SCHEDULER_CONFIGURATION_PARAMETERS: body_s[RES_SCHEDULER_CONFIGURATION_PARAMETERS],
        RES_CONFIGURATION_RUNNING_FUNCTIONS_MAX: body[RES_CONFIGURATION_RUNNING_FUNCTIONS_MAX],
        RES_HELLO_VERSION: body_h[RES_HELLO_VERSION]
    }


def start_suite(host, function_url, payload, start_lambda, end_lambda, lambda_delta, poisson, k, n_requests, out_dir,
                machine_id, save_req_times, verbose, debug=False):
    url = "http://{0}/{1}".format(host, function_url)

    pbs = []
    pes = []
    timings_total_time = []
    timings_srv_total_time = []
    timings_execution = []
    timings_scheduling = []
    timings_probing = []
    timings_forwarding = []
    probe_messages = []
    neterror_jobs = []

    current_lambda = start_lambda

    while True:
        test = FunctionTest(url, payload, current_lambda, k, poisson, n_requests, out_dir, machine_id, verbose, debug)
        test.execute_test()
        pbs.append(test.get_pb())
        pes.append(test.get_pe())

        timings_total_time.append(test.get_timings()[TIMING_TOTAL_TIME])
        timings_srv_total_time.append(test.get_timings()[TIMING_TOTAL_SRV_TIME])
        timings_execution.append(test.get_timings()[TIMING_EXECUTION_TIME])
        timings_scheduling.append(test.get_timings()[TIMING_SCHEDULING_TIME])
        timings_probing.append(test.get_timings()[TIMING_PROBING_TIME])
        timings_forwarding.append(test.get_timings()[TIMING_FORWARDING_TIME])

        probe_messages.append(test.get_probe_messages())
        neterror_jobs.append(test.get_net_errors())

        if save_req_times:
            test.save_request_timings()

        if start_lambda > end_lambda:
            current_lambda = round(current_lambda - lambda_delta, 2)
            if current_lambda < end_lambda:
                break
        else:
            current_lambda = round(current_lambda + lambda_delta, 2)
            if current_lambda > end_lambda:
                break

    def print_res():
        features = FunctionTest.get_features()

        print("\n[RESULTS] From lambda = %.2f to lambda = %.2f:" % (start_lambda, end_lambda))

        out_file = open("{}/results.txt".format(out_dir), "w")

        print("# ", end="", file=out_file)
        for f in features:
            print("%s " % f, end="")
            print("%s " % f, end="", file=out_file)
        print("\n")
        print("\n", file=out_file)

        for i in range(len(pbs)):
            print("%.2f %.6f %.6f %.6f %.6f %.6f %.6f %.6f %.6f %d" %
                  (start_lambda + i * lambda_delta, pbs[i], pes[i], timings_total_time[i], timings_srv_total_time[i],
                   timings_scheduling[i], timings_execution[i], timings_probing[i], timings_forwarding[i],
                   neterror_jobs[i]))
            print("%.2f %.6f %.6f %.6f %.6f %.6f %.6f %.6f %.6f %d" %
                  (start_lambda + i * lambda_delta, pbs[i], pes[i], timings_total_time[i], timings_srv_total_time[i],
                   timings_scheduling[i], timings_execution[i], timings_probing[i], timings_forwarding[i],
                   neterror_jobs[i]),
                  file=out_file)

        out_file.close()

    print_res()


def main(argv):
    host = ""
    function_url = ""
    start_lambda = -1
    end_lambda = -1
    lambda_delta = 0.5
    debug = False
    payload = ""
    poisson = False
    requests_n = 500
    out_dir = ""
    machine_id = 0
    save_req_times = False
    verbose = False

    usage = "multi_get.py"
    try:
        opts, args = getopt.getopt(
            argv, "hdm:u:p:k:t:", ["host=",
                                   "function-url=",
                                   "lambda-delta=",
                                   "start-lambda=",
                                   "end-lambda=",
                                   "mi=",
                                   "debug",
                                   "poisson",
                                   "requests=",
                                   "config-url=",
                                   "payload=",
                                   "out-dir=",
                                   "machine-id=",
                                   "save-req-timings",
                                   "verbose"
                                   ])
    except getopt.GetoptError:
        print(usage)
        sys.exit(2)
    for opt, arg in opts:
        # print(opt + " -> " + arg)
        if opt == '-h':
            print(usage)
            sys.exit()
        elif opt in ("-d", "--debug"):
            debug = True
        elif opt in "--host":
            host = arg
        elif opt in "--function-url":
            function_url = arg
        elif opt in "--lambda-delta":
            lambda_delta = float(arg)
        elif opt in "--start-lambda":
            start_lambda = float(arg)
        elif opt in "--end-lambda":
            end_lambda = float(arg)
        elif opt in ("-p", "--payload"):
            payload = arg
        elif opt in "--poisson":
            poisson = True
        elif opt in ("-t", '--requests'):
            requests_n = int(arg)
        elif opt in "--out-dir":
            out_dir = arg
        elif opt in "--machine-id":
            machine_id = int(arg)
        elif opt in "--save-req-timings":
            save_req_times = True
        elif opt in "--verbose":
            verbose = True

    if out_dir == "":
        time_str = strftime("%m%d%Y-%H%M%S", localtime())
        out_dir = "./_{}-{}".format(SCRIPT_NAME, time_str)
    os.makedirs(out_dir, exist_ok=True)

    print("=" * 10 + " Starting test suite " + "=" * 10)
    print("> host %s" % host)
    print("> debug %s" % debug)
    print("> function_url %s" % function_url)
    print("> payload %s" % payload)
    print("> lambda [%.2f,%.2f]" % (start_lambda, end_lambda))
    print("> lambda_delta %.2f" % lambda_delta)
    print("> requests_n %d" % requests_n)
    print("> use poisson %s" % ("yes" if poisson else "no"))
    print("> out_dir %s" % out_dir)
    print("> machine_id %d" % machine_id)
    print("> save_req_times %s" % ("yes" if save_req_times else "no"))

    if start_lambda < 0 or end_lambda < 0 or lambda_delta < 0 or function_url == "" or host == "":
        print("Some needed parameter was not given")
        print(usage)
        sys.exit()

    params = get_system_params(host)
    k = int(params[RES_CONFIGURATION_RUNNING_FUNCTIONS_MAX])
    print("-" * 10 + " system info " + "-" * 10)
    print("> scheduler name %s:%s" % (
        params[RES_SCHEDULER_CONFIGURATION_NAME], params[RES_SCHEDULER_CONFIGURATION_PARAMETERS]))
    print("> version %s" % params[RES_HELLO_VERSION])
    print("> k %d" % k)
    print("\n")

    if k < 0 or k == 0:
        print("Received bad k from server")
        print(usage)
        sys.exit()

    start_suite(host, function_url, payload, start_lambda, end_lambda,
                lambda_delta, poisson, k, requests_n, out_dir, machine_id, save_req_times, verbose, debug=debug)


if __name__ == "__main__":
    main(sys.argv[1:])
