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


WORKING_DIR = "/Users/gabrielepmattia/Coding/p2p-faas/experiments-data/BladeServers/PigoFaceDetectF/LL-PS(1,K)/20000reqs-8"
N_MACHINES = 8
MAX_T = 11
MIN_T = 0
N_REQUESTS = 20000

working_path = Path(WORKING_DIR)
dirs_list = sorted([f for f in working_path.glob('*') if f.is_dir()])

pb_list = []
delays_list = []

# loop over all values of T
for i in range(len(dirs_list)):
    t = MAX_T - i
    print("> Parsing T=%d in %s" % (t, dirs_list[i]))
    print(">> Average of %d machines" % N_MACHINES)
    total_pb = 0.0
    total_delay = 0.0
    for j in range(N_MACHINES):
        values_files = open("{}/results-machine-{:02d}.txt".format(dirs_list[i], j), "r")
        # pick only first line
        for line in values_files:
            values = line.split(" ")
            total_pb += float(values[1])
            total_delay += float(values[2])
            break
        values_files.close()
    pb_list.append(total_pb / N_MACHINES)
    delays_list.append(total_delay / N_MACHINES)

pb_list.reverse()
delays_list.reverse()

print("> Saving to out file")
out_file = open("{}/{}".format(WORKING_DIR, "multi_t.txt"), "w")
# print to file the list
for i in range(len(dirs_list)):
    accepted = math.ceil(N_REQUESTS * (1 - pb_list[i]))
    rejected = math.floor(N_REQUESTS * pb_list[i])
    print("%d %.6f %.6f %d %d" % (i, pb_list[i], delays_list[i], accepted, rejected), file=out_file)
out_file.close()

# plot
plot([i for i in range(MAX_T + 1)], pb_list, "T", "$P_B$", "multi_t_pb")
plot([i for i in range(MAX_T + 1)], delays_list, "T", "Delay", "multi_t_delay")
