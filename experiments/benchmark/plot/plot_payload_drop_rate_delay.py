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

import os
import sqlite3
from sqlite3 import Cursor

from utils import DBUtils, PlotUtils, Plot

LOG_FILE = "../log/02012022-095516.db"

N_NODES = 6

LAMBDA_FROM = 2.0
LAMBDA_TO = 3.0
LAMBDA_DELTA = 0.2

PAYLOAD_FILE_NAME = "family"
PAYLOAD_FILE_EXT = "jpg"
PAYLOAD_SIZES = [
    50000,
    100000,
    200000,
    300000,
    400000,
    500000,
    600000,
    700000,
    800000
]

PAYLOAD_RETURN_SIZE = 133000  # bytes

db = sqlite3.connect(LOG_FILE)
cur = db.cursor()

# compute drop rate
current_lambda = LAMBDA_FROM

os.makedirs("plot", exist_ok=True)


def get_payload_name(size):
    return f"{PAYLOAD_FILE_NAME}_{size}bytes.{PAYLOAD_FILE_EXT}"


def get_avg_time_total(cur, payload_size, current_lambda):
    return DBUtils.execute_query_for_float(cur, f'''
                        select 
                            avg("dropped")
                        from 
                            (select node_id, avg("time_total") as "dropped" 
                                from jobs 
                                where status_code = 200 
                                    and requests_rate = {current_lambda:.1f} 
                                    and payload_name = "{get_payload_name(payload_size)}" 
                                group by node_id
                            )
                        ''')


def get_avg_time_execution(cur, payload_size, current_lambda):
    return DBUtils.execute_query_for_float(cur, f'''
                        select 
                            avg("dropped")
                        from 
                            (select node_id, avg("time_execution") as "dropped" 
                                from jobs 
                                where status_code = 200 
                                    and requests_rate = {current_lambda:.1f} 
                                    and payload_name = "{get_payload_name(payload_size)}" 
                                group by node_id
                            )
                        ''')


def get_drop_rate(cur, payload_size, current_lambda):
    return DBUtils.execute_query_for_float(cur, f'''
                        select 
                            avg("dropped")
                        from 
                            (select node_id, count(*) as "dropped" 
                                from jobs 
                                where status_code = 500 
                                    and requests_rate = {current_lambda:.1f} 
                                    and payload_name = "{get_payload_name(payload_size)}" 
                                group by node_id
                            )
                        ''')


def get_total_jobs(cur, payload_size, current_lambda):
    return DBUtils.execute_query_for_integer(cur, f'''
                 select 
                        avg("dropped")
                    from 
                        (select node_id, count(*) as "dropped" 
                            from jobs 
                            where requests_rate = {current_lambda:.1f}
                                and payload_name = "{get_payload_name(payload_size)}" 
                            group by node_id
                        )
                    ''')


def get_avg_tau(cur: Cursor, payload_size, current_lambda):
    res = cur.execute(f'''
                select 
                    jobs.node_id, jobs.req_id, jobs.requests_rate, jobs.status_code, jobs.time_total, timings.time_type, timings.time_value, timings.index_i
                from
                    jobs join timings on jobs.node_id = timings.node_id 
                    and jobs.requests_rate = timings.requests_rate 
                    and jobs.payload_name = timings.payload_name 
                    and jobs.req_id = timings.req_id
                where
                    jobs.externally_executed = 1
                    and jobs.requests_rate = {current_lambda:.1f}
                    and jobs.payload_name = "{get_payload_name(payload_size)}" 
                order by 
                    jobs.node_id, jobs.req_id
                ''')
    taus = []

    cur_node_id = -1
    cur_req_id = -1

    service_time_node_a = 0.0
    service_time_node_b = 0.0
    probing_time_node_a = 0.0
    init = False

    for line in res:
        node_id = line[0]
        req_id = line[1]

        time_type = line[5]
        time_value = line[6]
        time_index_i = line[7]

        # print(f"node_id={node_id} req_id={req_id} time_type={time_type} time_value={time_value} time_index_i={time_index_i}")

        if node_id != cur_node_id or cur_req_id != req_id:
            cur_req_id = req_id
            cur_node_id = node_id

            if init is True:
                # compute tau
                forwarding_perc = payload_size / (payload_size + PAYLOAD_RETURN_SIZE)
                forwarding_time = (service_time_node_a - service_time_node_b - probing_time_node_a) * forwarding_perc
                tau_time = probing_time_node_a / 2 + forwarding_time
                taus.append(tau_time)
                # print(f"tau_time={tau_time} service_time_node_a={service_time_node_a} "
                #       f"service_time_node_b={service_time_node_b} probing_time_node_a={probing_time_node_a} "
                #       f"forwarding_perc={forwarding_perc}")

            init = True

        if time_index_i == 0:
            if time_type == "service":
                service_time_node_a = time_value
            if time_type == "probing":
                probing_time_node_a = time_value
        if time_index_i == 1:
            if time_type == "service":
                service_time_node_b = time_value

    return (sum(taus) / len(taus)) * 1000  # ms


X = []
Y_drop_rate = []
Y_time_total = []
Y_time_execution = []
legend = []

X_tau = []

while True:
    legend.append(fr"$\lambda$ = {current_lambda:.1f}")

    payload_x = []
    payload_y_drop_rate = []
    payload_y_time_total = []
    payload_y_time_execution = []

    tau_x = []

    # for i in range(N_NODES):
    for payload_size in PAYLOAD_SIZES:
        payload_name = get_payload_name(payload_size)

        dropped_jobs_avg = get_drop_rate(cur, payload_size, current_lambda)
        total_jobs_average = get_total_jobs(cur, payload_size, current_lambda)

        avg_time_total = get_avg_time_total(cur, payload_size, current_lambda)
        avg_time_execution = get_avg_time_execution(cur, payload_size, current_lambda)

        tau = get_avg_tau(cur, payload_size, current_lambda)

        payload_x.append(payload_size / 1000)
        payload_y_drop_rate.append(dropped_jobs_avg / total_jobs_average)
        payload_y_time_total.append(avg_time_total)
        payload_y_time_execution.append(avg_time_execution)

        tau_x.append(tau)

        print(f"retrieved current_lambda={current_lambda:.1f} dropped_jobs={dropped_jobs_avg:.2f} "
              f"total_jobs={total_jobs_average}, payload={get_payload_name(payload_size)}, tau={tau}")

    X.append(payload_x)
    X_tau.append(tau_x)
    Y_drop_rate.append(payload_y_drop_rate)
    Y_time_execution.append(payload_y_time_execution)
    Y_time_total.append(payload_y_time_total)

    current_lambda += LAMBDA_DELTA
    if round(current_lambda, 2) > LAMBDA_TO:
        break

PlotUtils.use_tex()
Plot.multi_plot(X, Y_drop_rate,
                x_label="Payload size (kb)",
                y_label="Drop Rate",
                filename="plot_payload_drop_rate", legend=legend)

Plot.multi_plot(X, Y_time_execution,
                x_label="Payload size (kb)",
                y_label="Time Execution (s)",
                filename="plot_payload_time_execution", legend=legend)

Plot.multi_plot(X, Y_time_total,
                x_label="Payload size (kb)",
                y_label="Time Total (s)",
                filename="plot_payload_time_total", legend=legend)

Plot.multi_plot(X_tau, Y_drop_rate,
                x_label=r"$\tau$ (ms)",
                y_label="Drop Rate",
                filename="plot_tau_drop_rate", legend=legend)

Plot.multi_plot(X_tau, Y_time_execution,
                x_label=r"$\tau$ (ms)",
                y_label="Time Execution (s)",
                filename="plot_tau_time_execution", legend=legend)

Plot.multi_plot(X_tau, Y_time_total,
                x_label=r"$\tau$ (ms)",
                y_label="Time Total (s)",
                filename="plot_tau_time_total", legend=legend)
