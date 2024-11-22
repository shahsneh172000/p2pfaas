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

from scipy import stats
import math
from matplotlib import pyplot as plt
from pathlib import Path

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
        + r"\usepackage[libertine]{newtxmath}"  # \usepackage[libertine]{newtxmath}\usepackage[T1]{fontenc}"
        + r"\usepackage[T1]{fontenc}"
        + ""]

WORKING_DIR = "/Users/gabrielepmattia/Coding/p2p-faas/experiments-data/BladeServers/PigoFaceDetectF/LL-PS(1,K)"
DIR_PREFIX = "20000reqs"

N_TESTS = 8
N_THRESHOLDS = 12

ALFA_VALUE = 0.10


def arr_average(arr):
    total = 0.0
    for v in arr:
        total += v
    return total / len(arr)


def arr_variance(arr, avg):
    total = 0.0
    for v in arr:
        total += pow(v - avg, 2)
    return total / (len(arr) - 1)


def plot_confidence(x_arr, y_arr, y_errors, x_label, y_label, filename, y_limits=None):
    plt.clf()
    fig, ax = plt.subplots()

    # for i in range(len(y_arr)):
    # ax.plot(x_arr, y_arr[1], marker="x", markersize=3.0, markeredgewidth=1, linewidth=0.7, color='C0')
    # ax.fill_between(x_arr, y_arr[0], y_arr[1], where=y_arr[0] >= y_arr[1], facecolor="C0", alpha=0.2)
    # ax.fill_between(x_arr, y_arr[0], y_arr[2], where=y_arr[0] <= y_arr[2], facecolor="C0", alpha=0.2)
    plt.errorbar(x_arr, y_arr[1], yerr=y_errors, marker="o", markersize=3.0, markeredgewidth=1, linewidth=0.7,
                 color='C0', capsize=2.5)  # mfc='none'

    if y_limits is not None:
        plt.ylim(y_limits)

    # ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    fig.tight_layout()
    plt.savefig("{}/{}.pdf".format(WORKING_DIR, filename))
    plt.close(fig)


pbs = [[] for _ in range(N_THRESHOLDS)]
delays = [[] for _ in range(N_THRESHOLDS)]
accepted = [[] for _ in range(N_THRESHOLDS)]
rejected = [[] for _ in range(N_THRESHOLDS)]

for i in range(0, N_TESTS):
    file_path = Path("{}/{}-{}/multi_t.txt".format(WORKING_DIR, DIR_PREFIX, i + 1))
    if not file_path.is_file():
        print("> [E] %s is not a file " % file_path)
        continue

    print("> Parsing %s" % file_path)
    values_file = open(file_path, "r")

    line_n = 0
    for line in values_file:
        values = line.split(" ")
        pbs[line_n].append(float(values[1]))
        delays[line_n].append(float(values[2]))
        accepted[line_n].append(float(values[3]))
        rejected[line_n].append(float(values[4]))
        line_n += 1
    values_file.close()

pbs_avgs = []
pbs_vars = []
pbs_upper = []
pbs_lower = []
pbs_errors = []

delays_avgs = []
delays_vars = []
delays_upper = []
delays_lower = []
delays_errors = []

accepted_avgs = []
accepted_vars = []
accepted_upper = []
accepted_lower = []
accepted_errors = []

rejected_avgs = []
rejected_vars = []
rejected_upper = []
rejected_lower = []
rejected_errors = []


def computeValues(i, arr, avgs, vars, upper, lower, errors):
    avgs.append(arr_average(arr[i]))
    vars.append(arr_variance(arr[i], avgs[i]))
    t_value = stats.t.ppf(1 - (ALFA_VALUE / 2), N_TESTS - 1) * math.sqrt(vars[i] / N_TESTS)
    errors.append(t_value)

    lower_value = avgs[i] - t_value

    upper.append(avgs[i] + t_value)
    lower.append(0.0 if round(lower_value, 2) < 0.0 else lower_value)


for i in range(N_THRESHOLDS):
    print("> Computing values for pb, T=%d" % i)
    computeValues(i, pbs, pbs_avgs, pbs_vars, pbs_upper, pbs_lower, pbs_errors)
    print("> Computing values for delays, T=%d" % i)
    computeValues(i, delays, delays_avgs, delays_vars, delays_upper, delays_lower, delays_errors)
    print("> Computing values for accepted, T=%d" % i)
    computeValues(i, accepted, accepted_avgs, accepted_vars, accepted_upper, accepted_lower, accepted_errors)
    print("> Computing values for rejected, T=%d" % i)
    computeValues(i, rejected, rejected_avgs, rejected_vars, rejected_upper, rejected_lower, rejected_errors)

print("> Plotting pb")
plot_confidence([i for i in range(N_THRESHOLDS)], [pbs_lower, pbs_avgs, pbs_upper], pbs_errors, "T", "$P_B$",
                "pbs_confidence", [0, 0.25])
print("> Plotting delays")
plot_confidence([i for i in range(N_THRESHOLDS)], [delays_lower, delays_avgs, delays_upper], delays_errors, "T",
                "Delay (s)", "delay_confidence")

print("> Plotting accepted")
plot_confidence([i for i in range(N_THRESHOLDS)], [accepted_lower, accepted_avgs, accepted_upper], accepted_errors, "T",
                "Accepted Requests", "accepted_confidence")
print("> Plotting rejected")
plot_confidence([i for i in range(N_THRESHOLDS)], [rejected_lower, rejected_avgs, rejected_upper], rejected_errors, "T",
                "Rejected Requests", "rejected_confidence")
