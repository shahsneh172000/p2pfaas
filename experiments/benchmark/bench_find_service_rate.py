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

import dataclasses
import mimetypes
import sqlite3
import time
from datetime import datetime
from threading import Thread, Lock
from typing import List

import requests

from log import Log

MACHINE_HOST = "192.168.50.100:18080"
FUNCTION_URL = "function/fn-pigo"
PAYLOAD_PATH = "./blobs/familyr_180p.jpg"
NUMBER_REQUESTS_PER_TEST = 500  # 1000
LAMBDA_MAX = 35.0  # 15.0
LAMBDA_MIN = 1.0  # 15.0
LOG_PATH = "./log"
N_TESTS = 10

_MODULE_NAME = "FindRate"

# db init
db_mutex = Lock()
db = sqlite3.connect(':memory:', check_same_thread=False)
db_cur = db.cursor()

db_cur.execute('''CREATE TABLE requests (
                     id_test integer, 
                     id_req integer, 
                     time_total real, 
                     time_execution real, 
                     requests_rate real,
                     status_code integer,
                     net_error integer
)''')


def current_time_string():
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def db_copy_to_file():
    print("Copying memory db to file, please wait")

    start = time.time()

    new_db = sqlite3.connect(f"{LOG_PATH}/find_service_rate_{current_time_string()}.db")
    query = "".join(line for line in db.iterdump())

    # Dump old database in the new one.
    new_db.executescript(query)
    new_db.close()

    print(f"Done in {time.time() - start:2f}")


def db_log_request(id_test, id_req, time_total, time_execution, requests_rate, status_code, net_error):
    db_mutex.acquire()

    # if results.node_id == 0:
    #     print(f"[TEST] db get_request node_id={results.node_id} req_id={results.req_id:4d}")

    db_cur.execute(f'''INSERT INTO requests VALUES (
                                    {id_test},
                                    {id_req},
                                    {time_total},
                                    {time_execution},
                                    {requests_rate},
                                    {status_code},
                                    {1 if net_error else 0}
                        )''')

    db.commit()

    db_mutex.release()


@dataclasses.dataclass(init=False)
class CurrentResults:
    current_timings: List[float]
    current_net_errors: int = 0
    current_not_succeeded: int = 0
    current_mutex = Lock()


def read_binary(uri):
    if uri == "" or uri is None:
        return None

    in_file = open(uri, "rb")  # opening for [r]eading as [b]inary
    data = in_file.read()  # if you only wanted to read 512 bytes, do .read(512)
    in_file.close()

    return data


payload_bin = read_binary(PAYLOAD_PATH)
payload_mime = mimetypes.guess_type(PAYLOAD_PATH)[0]


def get_request(test_id, req_id, requests_rate, url, results: CurrentResults):
    Log.minfo(_MODULE_NAME, f"[FIND] test_id={test_id} req_id={req_id} started request to {url}")
    try:
        time_start = time.time()
        headers = {
            'Content-Type': payload_mime,
            # 'Connection': 'Keep-Alive',
            'X-P2pfaas-Scheduler-Bypass': 'true',
        }
        res = requests.post(url, data=payload_bin, headers=headers)
        if res.status_code != 200:
            results.current_not_succeeded += 1
        time_total = time.time() - time_start

        time_execution = 0.0
        if res.status_code == 200:
            time_execution = float(res.headers["X-P2pfaas-Timing-Execution-Time-Seconds"])

        Log.minfo(_MODULE_NAME, f"[FIND] test_id={test_id} req_id={req_id} end request to {url}: {time_total:.3f}")

        db_log_request(test_id, req_id, time_total, time_execution, requests_rate, res.status_code, False)
        # results.current_mutex.acquire()
        # results.current_timings.append(time_total)
        # results.current_mutex.release()
    except Exception as e:
        Log.merr(_MODULE_NAME, f"[FIND] test_id={test_id} req_id={req_id} error request to {url}: {e}")
        db_log_request(test_id, req_id, .0, .0, requests_rate, -1, True)
        # results.current_mutex.acquire()
        # results.current_net_errors += 1
        # results.current_mutex.release()


res_lambdas = []
res_avg_times = []
res_net_errors = []
res_not_succeeded = []
res_avg_ros = []

for test_id in range(N_TESTS):

    current_l = LAMBDA_MIN

    while True:
        threads = []
        results = CurrentResults()
        results.current_timings = []

        # test the current lambda
        for req_id in range(NUMBER_REQUESTS_PER_TEST):
            Log.minfo(_MODULE_NAME,
                      f"[FIND] test_id={test_id} req_id={req_id} generating request {req_id} at rate={current_l}")

            time_start = time.time()

            t = Thread(target=get_request,
                       args=(test_id, req_id, current_l, f"http://{MACHINE_HOST}/{FUNCTION_URL}", results))
            threads.append(t)
            t.start()

            time_total = time.time() - time_start

            if time_total < 1 / current_l:
                # wait the remaining time
                time.sleep((1 / current_l) - time_total)
            else:
                Log.merr(_MODULE_NAME, f"cannot generate requests at rate={current_l}")

        for t in threads:
            t.join()

        # compute average timings
        res_lambdas.append(current_l)
        res_net_errors.append(results.current_net_errors)
        res_not_succeeded.append(results.current_not_succeeded)

        if len(results.current_timings) > 0:
            avg_time = sum(results.current_timings) / len(results.current_timings)
            res_avg_times.append(avg_time)

            res_avg_ros.append(current_l * avg_time)
        else:
            res_avg_times.append(0.0)

        # Log.minfo(_MODULE_NAME, f"[FIND] compute average for "
        #                         f"rate={current_l}, "
        #                         f"avg_times={res_avg_times[-1]}, "
        #                         f"avg_ros={res_avg_ros[-1]}, "
        #                         f"net_errors={results.current_net_errors} "
        #                         f"not_succeeded={results.current_not_succeeded} "
        #                        f"")

        # increase lambda
        current_l = round(current_l + 1.0, 2)
        if current_l > LAMBDA_MAX:
            break

        Log.minfo(_MODULE_NAME, f"[FIND] switched to rate={current_l}")

db_copy_to_file()

# print(res_lambdas)
# print(res_avg_times)
# print(res_net_errors)
# print(res_not_succeeded)
# print(res_avg_ros)

# PlotUtils.use_tex()

"""
def plot_barchart(arr, tag):
    def addlabels(x, y):
        for i in range(len(x)):
            plt.text(i, y[i], y[i], ha='center')

    x = res_lambdas
    y = arr

    Plot.plot(x, y, "", "", "", title=tag, full_path=f"./plot/plot/bar_{tag}_{Utils.current_time_string()}.pdf")
"""

# plot_barchart(res_avg_times, "avg_times")
# plot_barchart(res_net_errors, "net_errors")
# plot_barchart(res_not_succeeded, "not_succeeded")
# plot_barchart(res_avg_ros, "avg_ros")
