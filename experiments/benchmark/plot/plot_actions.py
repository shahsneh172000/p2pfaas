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

from plot.plot_reward_delay_multi_node import get_start_time, get_end_time
from plot.utils import PlotUtils, Plot, Utils

DB_FILENAME = "20220408-095722"
LOG_FILE = f"../log/{DB_FILENAME}.db"

N_NODES = 12
N_ACTIONS = 13

BASE_LEGEND = ["Reject", "Execute Locally"]

db = sqlite3.connect(LOG_FILE)
cur = db.cursor()

os.makedirs("plot", exist_ok=True)


def get_query_action_per_second(node_id, action):
    return f'''
            select
                cast(timestamp_start as integer), count(*) 
            from 
                jobs 
            where 
                node_id = {node_id}
                and learning_action = {action:.1f} 
            group by cast(timestamp_start as integer)
            order by cast(timestamp_start as integer)
            '''


def get_query_actions_per_second(node_id):
    return f'''
            select
                cast(timestamp_start as integer), cast(learning_action as integer), count(*) 
            from 
                jobs 
            where 
                node_id = {node_id}
            group by cast(timestamp_start as integer), cast(learning_action as integer) 
            order by cast(timestamp_start as integer), cast(learning_action as integer)
            '''


def get_query_jobs_per_second(node_id):
    return f'''
            select
                cast(timestamp_start as integer), count(*) 
            from 
                jobs 
            where 
                node_id = {node_id}
            group by cast(timestamp_start as integer)
            order by cast(timestamp_start as integer)
            '''


time_start = get_start_time(cur)
time_end = get_end_time(cur)

simulation_time = time_end - time_start

print(f"time_start=${time_start} time_end=${time_end} total_time={int(simulation_time)}")

cur.close()

NODE = 0


def plot(node_id):
    print(f"==> Preparing Node {node_id}")

    db = sqlite3.connect(LOG_FILE)
    cur = db.cursor()

    average_every_secs = 100

    time_actions = {}  # { 0: {action: num} }

    # get actions and jobs per second
    res_actions = cur.execute(get_query_actions_per_second(node_id))

    print(f"DB for Node {node_id}")
    for line in res_actions:
        t = int(line[0]) - time_start
        action = int(line[1])
        jobs = int(line[2])

        # print(f"t = {t}")

        if t not in time_actions.keys():
            time_actions[t] = {}
            for i in range(N_ACTIONS):
                time_actions[t][i] = 0

        time_actions[t][action] += jobs

    accumulator = {}

    x_arr = [[] for _ in range(N_ACTIONS)]
    y_arr = [[] for _ in range(N_ACTIONS)]

    print(f"Sum for Node {node_id}")
    for t in range(int(simulation_time)):
        # print(f"t = {t}")

        # reset the accumulator
        if t % average_every_secs == 0:
            for a in range(N_ACTIONS):
                accumulator[a] = 0

            # the last is the total sum
            accumulator[N_ACTIONS] = 0

        # sum actions
        if t in time_actions:
            for a in range(N_ACTIONS):
                accumulator[a] += time_actions[t][a]
                accumulator[N_ACTIONS] += time_actions[t][a]

        # add point to chart
        if t > 0 and t % average_every_secs - 1 == 0:
            for a in range(N_ACTIONS):
                x_arr[a].append(t)
                y_arr[a].append(accumulator[a] / accumulator[N_ACTIONS])

    cur.close()
    db.close()

    PlotUtils.use_tex()

    print(f"Plotting Node {node_id}, len(x_arr)={len(x_arr)} len(y_arr)={len(y_arr)}")

    node_legend = []
    for action in BASE_LEGEND:
        node_legend.append(action)

    for i in range(N_NODES):
        if i == node_id:
            continue

        node_legend.append(f"Frwd to {i}")

    Plot.multi_plot(x_arr, y_arr,
                    x_label="Time (s)",
                    y_label=r"\% of actions",
                    full_path=f"plot/plot_actions_{node_id}_db_{DB_FILENAME}_{Utils.current_time_string()}.pdf",
                    legend=node_legend)


for node_id in range(N_NODES):
    plot(node_id)
