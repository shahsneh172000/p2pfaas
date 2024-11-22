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

import os
from pathlib import Path
from matplotlib import pyplot as plt
import math

markers = [r"$\triangle$", r"$\square$", r"$\diamondsuit$", r"$\otimes$", r"$\oslash$"]
USE_TEX = True

if USE_TEX:
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['text.usetex'] = True
    plt.rcParams['text.latex.preamble'] = [
        r"\DeclareUnicodeCharacter{03BB}{$\lambda$}"
        + r"\DeclareUnicodeCharacter{03BC}{$\mu$}"
        + r"\usepackage[utf8]{inputenc}"
        + r"\usepackage{amssymb}"
        # + r"\usepackage{libertine}\usepackage[libertine]{newtxmath}\usepackage[T1]{fontenc}"
        + ""]


def plot(x_arr, y_arr, x_label, y_label, filename):
    plt.clf()
    fig, ax = plt.subplots()
    line_experimental, = ax.plot(x_arr, y_arr, marker="x", markersize=3.0, markeredgewidth=1, linewidth=0.7)

    # ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    fig.tight_layout()
    plt.savefig("{}/{}.pdf".format(WORKING_DIR, filename))
    plt.close(fig)


BASE_DIR = "/home/gpm/Coding/p2p-faas/experiments-data-rpi-cluster"
WORKING_DIR = f"{BASE_DIR}/6rpi-2000req-th-2-blobs-10-k-4-pigo-l-5-50-no-scheduler/6rpi-2000req-th-2-blobs-10-k-4-pigo-l-5-50-no-scheduler-run-2"
N_MACHINES = 6

BLOB_SIZES = [50000]
for i in range(1, 10):
    BLOB_SIZES.append(i * 100000)
print(BLOB_SIZES)

N_REQUESTS = 2000

working_path = Path(WORKING_DIR)
dirs_list = sorted([f for f in working_path.glob('*') if f.is_dir()])

pb_list = []
pe_list = []
delays_list = []
probing_time_list = []
scheduling_time_list = []
forwarding_time_list = []

# loop over all values of T
for i in range(len(dirs_list)):
    blob_size = BLOB_SIZES[i]
    print("> Parsing blob_size=%d in %s" % (blob_size, dirs_list[i]))
    print(">> Average of %d machines" % N_MACHINES)
    total_pb = 0.0
    total_delay = 0.0
    total_probing_time = 0.0
    total_scheduling_time = 0.0
    total_forwarding_time = 0.0
    total_pe = 0.0
    for j in range(N_MACHINES):
        values_files = open("{}/results-machine-{:02d}.txt".format(dirs_list[i], j), "r")
        # pick only first line
        for line in values_files:
            values = line.split(" ")
            total_pb += float(values[1])
            total_pe += float(values[2])
            total_delay += float(values[3])
            total_scheduling_time += float(values[5])
            total_probing_time += float(values[7])
            total_forwarding_time += float(values[8])
            break
        values_files.close()
    pb_list.append(total_pb / N_MACHINES)
    pe_list.append(total_pe / N_MACHINES)
    delays_list.append(total_delay / N_MACHINES)
    probing_time_list.append(total_probing_time / N_MACHINES)
    scheduling_time_list.append(total_scheduling_time / N_MACHINES)
    forwarding_time_list.append(total_forwarding_time / N_MACHINES)

# pb_list.reverse()
# delays_list.reverse()

print("> Saving to out file")
out_file = open("{}/{}".format(WORKING_DIR, "multi_t.txt"), "w")
# print to file the list
for i in range(len(dirs_list)):
    accepted = math.ceil(N_REQUESTS * (1 - pb_list[i]))
    rejected = math.floor(N_REQUESTS * pb_list[i])
    print("%d %.6f %.6f %.6f %.6f %.6f %d %d" % (
        i, pb_list[i], delays_list[i], probing_time_list[i], scheduling_time_list[i], forwarding_time_list[i], accepted,
        rejected), file=out_file)
out_file.close()

print(len(pb_list))
print(len(delays_list))
print(len(probing_time_list))

# plot
plot([BLOB_SIZES[i] / 1000 for i in range(len(dirs_list))], pb_list,
     "Payload Size (kb)", "$P_B$", "multi_t_pb")
plot([BLOB_SIZES[i] / 1000 for i in range(len(dirs_list))], pe_list,
     "Payload Size (kb)", "$P_e$", "multi_t_pe")
plot([BLOB_SIZES[i] / 1000 for i in range(len(dirs_list))], delays_list,
     "Payload Size (kb)", "Delay (s)", "multi_t_delay")
plot([BLOB_SIZES[i] / 1000 for i in range(len(dirs_list))], probing_time_list,
     "Payload Size (kb)", "Probing Time (s)", "multi_t_probing")
plot([BLOB_SIZES[i] / 1000 for i in range(len(dirs_list))], scheduling_time_list,
     "Payload Size (kb)", "Scheduling Time (s)", "multi_t_scheduling")
plot([BLOB_SIZES[i] / 1000 for i in range(len(dirs_list))], forwarding_time_list,
     "Payload Size (kb)", "Forwarding Time (s)", "multi_t_forwarding")
