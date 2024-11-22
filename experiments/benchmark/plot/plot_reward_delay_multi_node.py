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

import matplotlib.pyplot as plt

from plot.utils import DBUtils, PlotUtils, Utils

DB_FILENAME = "20220511-221732"
DB_FILENAME_2 = "20220512-003147"
DB_FILENAME_3 = "20220412-124726"

# DB_FILENAME = "20220412-073020"
# DB_FILENAME_2 = "20220412-112014"
# DB_FILENAME_3 = "20220412-124726"

LOG_FILE = f"../log/{DB_FILENAME}.db"
LOG_FILE_2 = f"../log/{DB_FILENAME_2}.db"
LOG_FILE_3 = f"../log/{DB_FILENAME_3}.db"

LOG_FILES = [
    LOG_FILE,
    LOG_FILE_2,
]

IPS = [
    "192.168.50.100",
    "192.168.50.101",
    "192.168.50.102",
    "192.168.50.103",
    "192.168.50.104",
    "192.168.50.105",
    "192.168.50.106",
    "192.168.50.107",
    "192.168.50.110",
    "192.168.50.111",
    "192.168.50.112",
    "192.168.50.113",
]

N_NODES = 12

LAMBDA_FROM = 5.0
LAMBDA_TO = 5.0
LAMBDA_DELTA = 0.2

os.makedirs("plot", exist_ok=True)


def get_query_avg_iota_per_second(cur, current_lambda, node_id):
    return f'''
            select
                cast(timestamp_start as integer), sum(learning_reward)/count(*) 
            from 
                jobs 
            where 
                node_id = {node_id} 
                -- and requests_rate = {current_lambda}
            group by cast(timestamp_start as integer)
            order by cast(timestamp_start as integer)
            '''


def get_query_avg_eps_per_second(cur, current_lambda, node_id):
    return f'''
            select
                cast(timestamp_start as integer), avg(learning_eps)
            from 
                jobs 
            where 
                node_id = {node_id} 
                -- and requests_rate = {current_lambda}
            group by cast(timestamp_start as integer)
            order by cast(timestamp_start as integer)
            '''


def get_query_avg_reward_per_second(cur, current_lambda, node_id):
    return f'''
            select
                cast(timestamp_start as integer), sum(learning_reward) 
            from 
                jobs 
            where 
                node_id = {node_id} 
                -- and requests_rate = {current_lambda}
            group by cast(timestamp_start as integer)
            order by cast(timestamp_start as integer)
            '''


def get_query_avg_delay_per_second(cur, current_lambda, node_id):
    return f'''
            select
                cast(timestamp_start as integer), avg(time_total) 
            from 
                jobs 
            where 
                node_id = {node_id} 
                and res_status_code = 200
                -- and requests_rate = {current_lambda}
            group by cast(timestamp_start as integer)
            order by cast(timestamp_start as integer)
            '''


def get_query_avg_rejected_per_second(cur, current_lambda, node_id):
    return f'''
            select
                cast(timestamp_start as integer), count(*) 
            from 
                jobs 
            where 
                node_id = {node_id}
                and (res_status_code = 500 or res_status_code = 503)
                -- and requests_rate = {current_lambda}
            group by cast(timestamp_start as integer)
            order by cast(timestamp_start as integer)
            '''


def get_query_avg_rejected_deliberately_per_second(cur, current_lambda, node_id):
    return f'''
            select
                cast(timestamp_start as integer), count(*) 
            from 
                jobs 
            where 
                node_id = {node_id}
                and (res_status_code = 503)
                -- and requests_rate = {current_lambda}
            group by cast(timestamp_start as integer)
            order by cast(timestamp_start as integer)
            '''


def get_query_avg_rejected_forcefully_per_second(cur, current_lambda, node_id):
    return f'''
            select
                cast(timestamp_start as integer), count(*) 
            from 
                jobs 
            where 
                node_id = {node_id}
                and (res_status_code = 500)
                -- and requests_rate = {current_lambda}
            group by cast(timestamp_start as integer)
            order by cast(timestamp_start as integer)
            '''


def get_query_avg_received_per_second(cur, current_lambda, node_id):
    return f'''
            select
                cast(timestamp_start as integer), count(*) 
            from 
                jobs 
            where 
                node_id = {node_id}
                -- and requests_rate = {current_lambda}
            group by cast(timestamp_start as integer)
            order by cast(timestamp_start as integer)
            '''


def get_query_avg_succeeded_per_second(cur, current_lambda, node_id):
    return f'''
            select
                cast(timestamp_start as integer), count(*) 
            from 
                jobs 
            where 
                node_id = {node_id}
                and res_status_code = 200
                -- and requests_rate = {current_lambda}
            group by cast(timestamp_start as integer)
            order by cast(timestamp_start as integer)
            '''


def get_query_avg_errored_per_second(cur, current_lambda, node_id):
    return f'''
            select
                cast(timestamp_start as integer), count(*) 
            from 
                jobs 
            where 
                node_id = {node_id}
                and req_net_error > 0
                -- and requests_rate = {current_lambda}
            group by cast(timestamp_start as integer)
            order by cast(timestamp_start as integer)
            '''


def get_query_avg_externally_executed_per_second(cur, current_lambda, node_id):
    return f'''
            select
                cast(timestamp_start as integer), cast(sum(externally_executed) as real)/count(*) 
            from 
                jobs 
            where 
                node_id = {node_id}
                -- and externally_executed = 1
                -- and requests_rate = {current_lambda}
            group by cast(timestamp_start as integer)
            order by cast(timestamp_start as integer)
            '''


def get_query_avg_externally_sent_per_second(cur, current_lambda, node_id):
    return f'''
            select
                cast(timestamp_start as integer), count(*) 
            from 
                jobs 
            where 
                node_id = {node_id}
                and learning_action != 0.0 
                and learning_action != 1.0
                -- and externally_executed = 1
                -- and requests_rate = {current_lambda}
            group by cast(timestamp_start as integer)
            order by cast(timestamp_start as integer)
            '''


def get_query_avg_externally_succeeded_per_second(cur, current_lambda, node_id):
    return f'''
            select
                cast(timestamp_start as integer), count(*) 
            from 
                jobs 
            where 
                node_id = {node_id}
                and learning_action != 0.0 
                and learning_action != 1.0
                and res_status_code = 200
                -- and externally_executed = 1
                -- and requests_rate = {current_lambda}
            group by cast(timestamp_start as integer)
            order by cast(timestamp_start as integer)
            '''


def get_query_avg_externally_succeeded_per_second_percentage(cur, current_lambda, node_id):
    return f'''
            select 
                table_ext_jobs.time, cast(table_ext_jobs.ext_executed_jobs as real)/cast(table_jobs.arrived_jobs as real)
            from 
                (select
                    cast(timestamp_start as integer) as time, count(*) as ext_executed_jobs
                from 
                    jobs
                where 
                    node_id = {node_id}
                    and learning_action != 0.0 
                    and learning_action != 1.0
                    and res_status_code = 200
                group by cast(timestamp_start as integer)
                order by cast(timestamp_start as integer)) as table_ext_jobs
            
                left join 
            
                (select
                    cast(timestamp_start as integer) as time, count(*) as arrived_jobs
                from 
                    jobs 
                where 
                    node_id = {node_id}
                group by cast(timestamp_start as integer)
                order by cast(timestamp_start as integer)) as table_jobs on table_ext_jobs.time = table_jobs.time
            '''


def get_start_time(cur):
    return DBUtils.execute_query_for_float(cur, f'''
            select
                cast(timestamp_start as integer) 
            from 
                jobs 
            order by cast(timestamp_start as integer) asc 
            limit 1
            ''')


def get_req_id_from_time(cur, node_id, from_time):
    return DBUtils.execute_query_for_float(cur, f'''
            select 
                req_id
            from 
                jobs
            where 
                node_id = {node_id}
                and timestamp_start > {from_time}
            ORDER by req_id
            limit 1
            ''')


def get_end_time(cur):
    return DBUtils.execute_query_for_float(cur, f'''
            select
                cast(timestamp_start as integer) 
            from 
                jobs 
            order by cast(timestamp_start as integer) desc 
            limit 1
            ''')


def get_last_seconds_jobs(cur, from_time, node_id):
    return f'''
            select
                * 
            from 
                jobs 
            where 
                node_id = {node_id}
                and timestamp_start >= {from_time:.1f} 
            '''


def get_forwarded_tasks(node_id, to_ip, from_req_id, to_req_id):
    query = f'''
            select 
                count(*)
            from 
                values_strings 
            where 
                node_id = {node_id}
                and index_i = 1 
                and value_value = "{to_ip}"
                and req_id > cast({from_req_id} as real)
                and req_id < cast({to_req_id} as real)
            '''

    return query


#
# Start
#

def compute_stats():
    last_seconds = 200

    PARAM_REWARD = "reward/jobs"
    PARAM_TIME_TOTAL = "time_total (s)"
    PARAM_TIME_EXECUTION = "time_execution (s)"
    PARAM_EXEC_EXT = "forwarded %"
    PARAM_REJECT_PERC = "rejected %"
    PARAM_TOTAL_JOBS = "total_jobs"

    VALUE_MEAN = "mean"
    VALUE_VAR = "var"

    PARAMS = [PARAM_TOTAL_JOBS, PARAM_REWARD, PARAM_TIME_TOTAL, PARAM_TIME_EXECUTION, PARAM_EXEC_EXT, PARAM_REJECT_PERC]

    all_results = {}

    for log_file in LOG_FILES:
        all_results[log_file] = {}

        db = sqlite3.connect(log_file)
        cur = db.cursor()

        time_start = get_start_time(cur)
        time_end = get_end_time(cur)

        time_for_stats = time_end - last_seconds

        final_res = {}  # node: param: mean/var

        for node_i in range(N_NODES):
            res = cur.execute(get_last_seconds_jobs(cur, time_for_stats, node_i))
            final_res[node_i] = {}
            arrays = {}  # param: [array]

            for param in PARAMS:
                if param == PARAM_TOTAL_JOBS:
                    arrays[param] = 0
                    final_res[node_i][param] = 0  # mean and variance
                else:
                    arrays[param] = []
                    final_res[node_i][param] = [0.0, 0.0]  # mean and variance

            for job in res:
                for param in PARAMS:
                    if param == PARAM_REWARD:
                        arrays[PARAM_REWARD].append(job[18])
                    if param == PARAM_TIME_TOTAL:
                        arrays[PARAM_TIME_TOTAL].append(job[5])
                    if param == PARAM_TIME_EXECUTION:
                        arrays[PARAM_TIME_EXECUTION].append(job[6])
                    if param == PARAM_EXEC_EXT:
                        arrays[PARAM_EXEC_EXT].append(job[12])
                    if param == PARAM_REJECT_PERC:
                        arrays[PARAM_REJECT_PERC].append(1 if int(job[8]) >= 500 else 0)
                    if param == PARAM_TOTAL_JOBS:
                        arrays[PARAM_TOTAL_JOBS] += 1

            for param in PARAMS:
                array = np.array(arrays[param])
                if param == PARAM_REWARD or param == PARAM_EXEC_EXT or param == PARAM_REJECT_PERC:
                    final_res[node_i][param] = [np.sum(array) / arrays[PARAM_TOTAL_JOBS], 0.0]
                else:
                    final_res[node_i][param] = [np.mean(array), np.var(array)]

        all_results[log_file] = final_res

    print(all_results)

    for log_file in LOG_FILES:
        print(f"\n===== LOG FILE {log_file} =====")

        print(f"{'parameter':20s} |", end="")
        for node_i in range(N_NODES):
            print(f"{'Node ' + str(node_i):>10s}\t", end="")
        print(f"{'Mean':>10s}\t", end="")
        print(f"{'Variance':>10s}\t", end="")
        print()

        print("-" * 200)

        for param in PARAMS:
            print(f"{param:20s} |", end="")
            param_mean_arr = []
            for node_i in range(N_NODES):
                param_mean_arr.append(all_results[log_file][node_i][param][0])
                print(f"{all_results[log_file][node_i][param][0]:10.4f}\t", end="")

            mean = np.mean(np.array(param_mean_arr))
            var = np.var(np.array(param_mean_arr))

            print(f"| {mean:10.4f} {var:10.4f}")


def compute_forwarded_stats():
    all_data = {}

    for log_file in LOG_FILES:
        db = sqlite3.connect(log_file)
        cur = db.cursor()

        start_time = get_start_time(cur)
        interval_start = 1800
        interval_end = 2800

        all_data[log_file] = {}

        for node_i in range(N_NODES):
            all_data[log_file][node_i] = {}
            summation_col = 0

            for ip in IPS:
                all_data[log_file][node_i][ip] = 0

                from_req_id = get_req_id_from_time(cur, node_i, interval_start + start_time)
                to_req_id = get_req_id_from_time(cur, node_i, interval_end + start_time)
                res = cur.execute(get_forwarded_tasks(node_i, ip, from_req_id, to_req_id))

                # print(f"node_i={node_i} from_req_id={from_req_id} to_req_id={to_req_id}")

                for line in res:
                    all_data[log_file][node_i][ip] = int(line[0])
                    summation_col += int(line[0])

            all_data[log_file][node_i]["sum_col"] = summation_col

        for ip in IPS:
            all_data[log_file][ip] = 0
            for node_i in range(N_NODES):
                all_data[log_file][ip] += all_data[log_file][node_i][ip]

    for log_file in LOG_FILES:
        print(f"\n===== FORWARED TASKS from {log_file} ======")
        print(f"ip\t\t\t\t\t|\t", end="")
        for node_i in range(N_NODES):
            print(f"{node_i} (%)", end="\t")
        print("\n", end="")
        print("-" * 140)

        for ip in IPS:
            print(ip, end="\t\t|\t")
            for node_i in range(N_NODES + 1):
                if node_i >= N_NODES:
                    print(f"|\t{all_data[log_file][ip]}", end="")
                else:
                    print(f"{100 * all_data[log_file][node_i][ip] / all_data[log_file][node_i]['sum_col']:02.2f}", end="\t")

            print("\n", end="")


def plot(query, plot_tag):
    d_x_values = {}
    d_y_values = {}

    y_lim = 0.0

    average_every_secs = 10

    for log_file in LOG_FILES:
        print(f"==> Parsing log file {log_file}")
        db = sqlite3.connect(log_file)
        cur = db.cursor()

        time_start = get_start_time(cur)
        time_end = get_end_time(cur)

        print(f"time_start=${time_start} time_end=${time_end} total_time={time_end - time_start}")

        d_x_values[log_file] = []
        d_y_values[log_file] = []

        for node_i in range(N_NODES):
            d_x_values[log_file].append([])
            d_y_values[log_file].append([])

            res = cur.execute(query(cur, LAMBDA_FROM, node_i))
            sum_reward = 0.0
            added = 0
            for line in res:
                t = int(line[0]) - time_start
                reward = line[1]

                sum_reward += reward
                added += 1

                if t % average_every_secs == 0 and t > 0:
                    # print(f"t={t}, added={added}, avg={sum_reward / added}")
                    y_value = sum_reward / added
                    d_x_values[log_file][node_i].append(t)
                    d_y_values[log_file][node_i].append(y_value)
                    added = 0
                    sum_reward = 0.0

                    y_lim = max(y_lim, 1.1 * y_value)

            print(f"Node#{node_i}: {d_y_values[log_file][node_i]}")

        cur.close()
        db.close()

    PlotUtils.use_tex()

    cmap_def = plt.get_cmap("tab10")
    fig, axis = plt.subplots(nrows=N_NODES, ncols=1)

    for node_i in range(N_NODES):
        # axis[node_i].set_title(rf"Node \#{node_i}")
        for log_file in LOG_FILES:
            print(f"Plotting log_file={log_file} x={d_x_values[log_file][node_i]}")
            print(f"Plotting log_file={log_file} y={d_y_values[log_file][node_i]}")
            axis[node_i].plot(d_x_values[log_file][node_i], d_y_values[log_file][node_i], linewidth='1')
        # axis[node_i].plot(x_n_rewards[node_i], y_n_rewards[node_i], linewidth='1.2', color=cmap_def(1))
        # axis[node_i].set_ylabel(f"{plot_tag}/s")
        if node_i == N_NODES - 1:
            axis[node_i].legend(["Sarsa", "Pwr2 (T=2)"], fontsize=6, loc='lower left')
        axis[node_i].margins(0)
        axis[node_i].tick_params(axis='y', labelsize=8)
        axis[node_i].set_ylim(bottom=0, top=y_lim)
        # axis[node_i].set_xlim([0, time_end - time_start])
        axis[node_i].grid(color='#cacaca', linestyle='--', linewidth=0.5)
        axis[node_i].annotate(rf'N\#{node_i}', xy=(1.015, .5), xycoords="axes fraction", rotation="-90",
                              va="center", ha="center")

        if node_i != N_NODES - 1:
            axis[node_i].set_xticklabels([])
        else:
            axis[node_i].set_xlabel("Time (s)")

    """
    for i in range(N_NODES):
        axis[N_NODES].plot(x_traffics[i], y_traffics[i], linewidth='1', color=cmap_def(i))
    axis[N_NODES].set_ylim([0, 1])
    axis[N_NODES].set_xlabel("Time")
    axis[N_NODES].set_ylabel(r"$\rho$")
    axis[N_NODES].margins(0)
    axis[N_NODES].grid(color='#cacaca', linestyle='--', linewidth=0.5)
    axis[N_NODES].legend([f"To Node \#{i}" for i in range(N_NODES)], fontsize=3, loc='lower right')
    """

    # size and padding
    fig.tight_layout(h_pad=0)
    fig.set_figwidth(6)  # 6.4
    fig.set_figheight(6)  # 4.8
    fig.subplots_adjust(wspace=0, hspace=0.2)

    # plt.show()
    os.makedirs("plot", exist_ok=True)
    # plt.show()
    plt.savefig(f"plot/plot_{plot_tag}_multi_node-db_{DB_FILENAME}_{Utils.current_time_string()}.pdf")


def main():
    DO_PLOT = False

    if DO_PLOT:
        plot(get_query_avg_reward_per_second, "reward")
        plot(get_query_avg_delay_per_second, "delay")
        plot(get_query_avg_rejected_per_second, "reject")
        plot(get_query_avg_rejected_deliberately_per_second, "reject_deliberately")
        plot(get_query_avg_rejected_forcefully_per_second, "reject_forcefully")
        plot(get_query_avg_received_per_second, "received")
        plot(get_query_avg_succeeded_per_second, "succeeded")
        plot(get_query_avg_errored_per_second, "errored")
        plot(get_query_avg_iota_per_second, "iota")
        plot(get_query_avg_externally_executed_per_second, "ext_executed")
        plot(get_query_avg_externally_sent_per_second, "ext_sent")
        plot(get_query_avg_externally_succeeded_per_second, "ext_succeeded")
        plot(get_query_avg_externally_succeeded_per_second_percentage, "ext_succeeded_percentage")
        plot(get_query_avg_eps_per_second, "eps")

    compute_stats()
    compute_forwarded_stats()


if __name__ == "__main__":
    # main(sys.argv[1:])
    main()
