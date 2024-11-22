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
from matplotlib import pyplot as plt

from plot.utils import PlotUtils, Plot

EPS_START = 0.9
EPS_DECAY = 0.999
PLOT_DIRECTORY = "./plot"

REQUESTS_PER_SECOND = 8
TOTAL_SECONDS = 10000

eps_list = []
times = []

number_of_requests = 0
current_eps = EPS_START
for i in range(TOTAL_SECONDS):
    for j in range(REQUESTS_PER_SECOND):
        current_eps *= EPS_DECAY

    eps_list.append(current_eps)
    times.append(i)

    number_of_requests += REQUESTS_PER_SECOND

PlotUtils.use_tex()
Plot.plot(times, eps_list, x_label="time", y_label="eps", filename="calc_eps")

print(f"Total requests: {number_of_requests}")
print(f"Total time: {int(TOTAL_SECONDS / 60)}:{(TOTAL_SECONDS % 60)}")

# plot final on decay
DESIRED_END_TIME = 4000
DESIRED_END_TIMES = [4000]  # [1000, 2000, 4000, 6000, 8000]

REQUESTS_N = [1, 2, 4, 6, 6.5, 8, 10]
REQUESTS_N_REQS = [i * DESIRED_END_TIME for i in REQUESTS_N]

DECAY_END = 0.05
DECAY_START = 0.9

x_arr = []
y_arr = []

to_mark = []

for time in DESIRED_END_TIMES:
    min_reqs = min(REQUESTS_N) * time - 1000
    max_reqs = max(REQUESTS_N) * time + 1000

    print(f"min_reqs={min_reqs} max={max_reqs}")

    x = []
    y = []

    j = 0
    for i in range(min_reqs, max_reqs):
        if i == 0 or i % 10 == 0:
            x.append(i)
            y.append(pow(DECAY_END, (DECAY_END / DECAY_START) / i))

            if i in REQUESTS_N_REQS:
                to_mark.append(j)

            j += 1

    x_arr.append(x)
    y_arr.append(y)


# Plot.multi_plot(x_arr, y_arr, x_label="requests", y_label="decay", filename="calc_eps_decay", use_marker=False)

# points

def decay(end_time, decay_end, decay_start, l):
    return pow(decay_end, (decay_end / decay_start) / (end_time * l))


points_x = [req * DESIRED_END_TIME for req in REQUESTS_N]
points_y = [pow(DECAY_END, (DECAY_END / DECAY_START) / i) for i in points_x]

print(x_arr)
print(y_arr)
print(points_x)
print(points_y)

fig, ax = plt.subplots()
line_experimental, = ax.plot(x_arr[0], y_arr[0], linestyle='--', linewidth=1.2, markevery=to_mark, marker="o")
# ax.scatter(points_x, points_y)

for i in range(len(points_x)):
    ax.annotate(fr"{points_y[i]:.6f} ($\lambda$={REQUESTS_N[i]})",
                xy=(points_x[i], points_y[i]),
                xycoords="data",
                fontsize="small")

ax.set_xlabel("requests")
ax.set_ylabel("decay")
ax.grid(color='#cacaca', linestyle='--', linewidth=0.5)
fig.tight_layout()

plt.savefig(f"{PLOT_DIRECTORY}/calc_eps_decay.pdf")
plt.close(fig)
