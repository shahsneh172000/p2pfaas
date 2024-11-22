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

import os
import sqlite3

import numpy as np
from matplotlib import pyplot as plt
from scipy.stats import t as t_student

from plot.utils import PlotUtils, Utils
# from utils import PlotUtils, Utils

LOG_FILE = "../log/find_service_rate_20220409-131410_320p.db"
LOG_FILE_2 = "../log/find_service_rate_20220421-160523_180p.db"

LOG_FILES = [LOG_FILE, LOG_FILE_2]

D_TIMES = "times"
D_TIMES_EXECUTION = "times_execution"
D_REJECTED = "rejected"
D_NET_ERRORS = "net_errors"

D_KEYS = [D_TIMES, D_TIMES_EXECUTION, D_REJECTED, D_NET_ERRORS]

MAX_LAMBDA = 35
MIN_LAMBDA = 1
N_TESTS = 10
N_REQUESTS = 500


def query_point_for_rates():
    return '''
            select 
                id_test, requests_rate, avg(time_total), sum(net_error), avg(time_execution)
            from 
                requests 
            where
                status_code = 200
            group by id_test, requests_rate
            '''


def query_point_for_net_error():
    return '''
            select 
                id_test, requests_rate, sum(net_error)
            from 
                requests 
            group by id_test, requests_rate
            '''


def query_point_for_rejected():
    return '''
            select 
                id_test, requests_rate, count(*)
            from 
                requests 
            where
                status_code = 500
            group by id_test, requests_rate
            '''


os.makedirs("plot", exist_ok=True)

d_logfiles = {}

for log_file in LOG_FILES:

    db = sqlite3.connect(log_file)
    cur = db.cursor()

    d_times = {}  # lambda: [arr]
    d_times_execution = {}  # lambda: [arr]
    d_errors = {}  # lambda: [arr]
    d_rejected = {}  # lambda: [arr]

    rows = cur.execute(query_point_for_rates())
    for row in rows:
        id_test = row[0]
        requests_rate = row[1]
        avg_time = row[2]
        sum_error = row[3]
        avg_time_execution = row[4]

        req_rate_str = f"{requests_rate:.1f}"
        if req_rate_str not in d_times.keys():
            d_times[req_rate_str] = []
        if req_rate_str not in d_errors.keys():
            d_errors[req_rate_str] = []
        if req_rate_str not in d_times_execution.keys():
            d_times_execution[req_rate_str] = []

        d_times[req_rate_str].append(avg_time)
        d_errors[req_rate_str].append(sum_error)
        d_times_execution[req_rate_str].append(avg_time_execution)

    rows = cur.execute(query_point_for_rejected())
    for row in rows:
        id_test = row[0]
        requests_rate = row[1]
        rejected = row[2] / N_REQUESTS

        req_rate_str = f"{requests_rate:.1f}"
        if req_rate_str not in d_rejected.keys():
            d_rejected[req_rate_str] = []

        d_rejected[req_rate_str].append(rejected)

    d_logfiles[log_file] = {}
    d_logfiles[log_file][D_TIMES] = d_times
    d_logfiles[log_file][D_TIMES_EXECUTION] = d_times_execution
    d_logfiles[log_file][D_NET_ERRORS] = d_errors
    d_logfiles[log_file][D_REJECTED] = d_rejected

    cur.close()
    db.close()

# compute i.c.s
x = [float(v) for v in range(MIN_LAMBDA, MAX_LAMBDA + 1)]


def compute_ic(array):
    arr = np.array(array)
    n = len(arr)
    m = arr.mean()
    s = arr.std()
    dof = n - 1
    confidence = 0.99

    t_crit = np.abs(t_student.ppf((1 - confidence) / 2, dof))

    low_value = m - s * t_crit / np.sqrt(n)
    high_value = m + s * t_crit / np.sqrt(n)

    return low_value, m, high_value


def erlang_b(load, n_servers):
    inv = 1
    for m in range(1, n_servers + 1):  # range does not include the last number, so we need to add 1
        inv = 1 + m / load * inv
    return 1 / inv


d_values = {}

for log_file in LOG_FILES:
    d_values[log_file] = {}

    for d_key in D_KEYS:
        print(f"Parsing values from {log_file}:{d_key}={d_logfiles[log_file][d_key]}")

        d_values[log_file][d_key] = {'l': [], "m": [], "h": []}

        for req_rate in x:
            req_rate_str = f"{req_rate:.1f}"

            if req_rate_str in d_logfiles[log_file][d_key].keys():
                print(
                    f"Parsing values from {log_file}:{d_key}:{req_rate_str}={d_logfiles[log_file][d_key][req_rate_str]}")
                arr_times = np.array(d_logfiles[log_file][d_key][req_rate_str])
                value_low, value_m, value_high = compute_ic(arr_times)

                d_values[log_file][d_key]['l'].append(0 if (value_m - value_low) < 0 else value_m - value_low)
                d_values[log_file][d_key]['m'].append(value_m)
                d_values[log_file][d_key]['h'].append(value_high - value_m)
            else:
                d_values[log_file][d_key]['l'].append(0.0)
                d_values[log_file][d_key]['m'].append(0.0)
                d_values[log_file][d_key]['h'].append(0.0)

PlotUtils.use_tex()

print(x)

for d_key in D_KEYS:
    plt.clf()
    fig, ax = plt.subplots()
    #ax2 = ax.twinx()

    for i, log_file in enumerate(LOG_FILES):
        print(f"\nPlotting key={d_key} logfile={log_file} i={i} l={d_values[log_file][d_key]['l']}")
        print(f"Plotting key={d_key} logfile={log_file} i={i} m={d_values[log_file][d_key]['m']}")
        print(f"Plotting key={d_key} logfile={log_file} i={i} h={d_values[log_file][d_key]['h']}")
        if i == 0 or i == 1:
            ax.set_ylim(bottom=-0.05)
            if d_key == D_REJECTED:
                ax.set_ylim(bottom=0, top=1.0)
            if d_key == D_TIMES_EXECUTION:
                ax.set_ylim(bottom=0.0, top=.45)

            ax.errorbar(x, d_values[log_file][d_key]['m'],
                        yerr=[d_values[log_file][d_key]['l'], d_values[log_file][d_key]['h']],
                        marker="x" if i == 0 else "o", markersize=2.5, markeredgewidth=0.7,
                        linewidth=0.7, elinewidth=0.8, capsize=3, label="Image A" if i == 0 else "Image B")
        else:
            ax2.set_ylim(bottom=-0.05)
            if d_key == D_REJECTED:
                ax2.set_ylim(bottom=0, top=0.1)
            if d_key == D_TIMES_EXECUTION:
                ax2.set_ylim(bottom=0.0, top=.15)

            ax2.errorbar(x, d_values[log_file][d_key]['m'],
                         yerr=[d_values[log_file][d_key]['l'], d_values[log_file][d_key]['h']],
                         marker="o", markersize=2.5, markeredgewidth=0.7,
                         linewidth=0.7, elinewidth=0.8, capsize=3, color="orange", label="Image B")

    ax.legend(loc='upper left', fontsize=12)
    #ax2.legend(loc='upper right', fontsize=12)

    ax.set_xlabel(r"$\lambda$", fontsize=12)
    ax.set_ylabel("Value", fontsize=12)
    if d_key == D_REJECTED:
        ax.set_ylabel("$P_B$", fontsize=12)
    if d_key == D_TIMES_EXECUTION:
        ax.set_ylabel("$d_e$ (s)", fontsize=12)

    ax.grid(color='#cacaca', linestyle='--', linewidth=0.5)

    for label in ax.xaxis.get_majorticklabels():
        label.set_fontsize(12)
    for label in ax.yaxis.get_majorticklabels():
        label.set_fontsize(12)
#    for label in ax2.xaxis.get_majorticklabels():
#        label.set_fontsize(12)
#    for label in ax2.yaxis.get_majorticklabels():
#        label.set_fontsize(12)

    fig.tight_layout()

    full_path = f"./plot/find_service_rate_{d_key}_execution_{Utils.current_time_string()}.pdf"

    fig.tight_layout(h_pad=0)
    fig.set_figwidth(4)  # 6.4
    fig.set_figheight(4)  # 4.8

    plt.subplots_adjust(left=0.16, right=0.988, top=0.964, bottom=0.117, wspace=0.2, hspace=0.2)
    plt.savefig(full_path)
    # plt.show()
    plt.close(fig)
