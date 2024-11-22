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

#
# This module computes the average response time of a get, by sending requests in series.
#

import getopt
import math
import os
import requests
import sys
import time
import threading

from common import CC
from common import read_binary

SCRIPT_NAME = os.path.splitext(os.path.basename(__file__))[0]


def bench_rtt(host, function, payload, requests_num, save_times, parallel):
    url = "http://{}/{}".format(host, function)
    print("> function url is %s" % url)

    def get_request(i, j, times_parallel):
        start_time = time.time()

        payload_bin = None
        if payload != "":
            payload_bin = read_binary(payload)

        print("==> [GET] Number #" + str(i + 1))
        res = requests.post(url, data=payload_bin)

        end_time = time.time()
        total_time = end_time - start_time

        if res.status_code == 200:
            print(CC.OKGREEN + "==> [RES] Status to #" + str(i) + " is " +
                  str(res.status_code) + " Time " + str(total_time) + CC.ENDC)
        else:
            print(CC.FAIL + "==> [RES] Status " +
                  str(res.status_code) + " Time " + str(total_time) + CC.ENDC)

        times_parallel[j] = total_time
        return total_time

    times = []

    for i in range(requests_num):
        times_parallel = [0.0 for i in range(parallel)]
        threads = [None for i in range(parallel)]

        for j in range(parallel):
            threads[j] = threading.Thread(target=get_request, args=(i, j, times_parallel))
            # res_time = get_request(i, j)

        for j in range(parallel):
            threads[j].start()

        for j in range(parallel):
            threads[j].join()

        times.append(sum(times_parallel) / len(times_parallel))

    # do stats
    if save_times:
        file_times = open("times.txt", "w")

    total_time = 0
    for n in times:
        total_time += n

        if save_times:
            # noinspection PyUnboundLocalVariable
            print("%.6f" % n, file=file_times)

    if save_times:
        file_times.close()

    avg = total_time / requests_num

    print("\nMean response time is " + str(avg) + "ms")
    print("Max is %f and min is %f" % (max(times), min(times)))


#
# Entrypoint
#


def main(argv):
    host = ""
    function = ""
    payload = ""
    requests = 200
    save_times = False
    parallel = 1

    usage = "plot_times.py"
    try:
        opts, args = getopt.getopt(
            argv, "h", ["host=", "function=", "payload=", "requests=", "save-times", "parallel="])
    except getopt.GetoptError:
        print(usage)
        sys.exit(2)
    for opt, arg in opts:
        # print(opt + " -> " + arg)
        if opt == '-h':
            print(usage)
            sys.exit()
        elif opt in "--host":
            host = arg
        elif opt in "--function":
            function = arg
        elif opt in "--payload":
            payload = arg
        elif opt in "--requests":
            requests = int(arg)
        elif opt in "--parallel":
            parallel = int(arg)
        elif opt in "--save-times":
            save_times = True

    print("====== P2P-FOG Compute mean delay of function ======")
    print("> host %s" % host)
    print("> function %s" % function)
    print("> payload %s" % payload)
    print("> requests %d" % requests)
    print("> save_times %s" % save_times)
    print("> parallel %s" % parallel)  # number of parallel series request
    print("")

    if host == "" or function == "":
        print("Some needed parameter was not given")
        print(usage)
        sys.exit()

    bench_rtt(host, function, payload, requests, save_times, parallel)


if __name__ == "__main__":
    main(sys.argv[1:])
