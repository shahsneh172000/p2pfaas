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

from plot.utils import Plot

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

WORKING_DIR = "/home/gpm/Coding/p2p-faas/experiments-data-rpi-cluster"
DIR_PREFIX = "6rpi-2000req-th-2-blobs-10-k-4-pigo-l-5-50-no-scheduler/6rpi-2000req-th-2-blobs-10-k-4-pigo-l-5-50-no-scheduler-run"

BLOB_SIZES = [50000]
for i in range(1, 9):
    BLOB_SIZES.append(i * 100000)
print(BLOB_SIZES)

N_TESTS = 2
N_BLOBS = len(BLOB_SIZES)

ALFA_VALUE = 0.05


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


def plot_confidence(x_arr, y_arr, y_errors, x_label, y_label, filename, title=None, y_limits=None):
    plt.clf()
    fig, ax = plt.subplots()

    # for i in range(len(y_arr)):
    # ax.plot(x_arr, y_arr[1], marker="x", markersize=3.0, markeredgewidth=1, linewidth=0.7, color='C0')
    # ax.fill_between(x_arr, y_arr[0], y_arr[1], where=y_arr[0] >= y_arr[1], facecolor="C0", alpha=0.2)
    # ax.fill_between(x_arr, y_arr[0], y_arr[2], where=y_arr[0] <= y_arr[2], facecolor="C0", alpha=0.2)
    plt.errorbar(x_arr, y_arr[1],
                 yerr=y_errors, marker="o", markersize=3.0, markeredgewidth=1, linewidth=0.7, color='C0', capsize=2.5)

    for a, b in zip(x_arr, y_arr[1]):
        plt.text(a, b, f"{b:.3f}", verticalalignment='top', horizontalalignment='left', fontsize=8)

    if y_limits is not None:
        plt.ylim(y_limits)
    if title is not None:
        plt.title(title)

    # ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    fig.tight_layout()
    plt.savefig("{}/{}.pdf".format(WORKING_DIR, filename))
    plt.close(fig)


def save_confidence(x_arr, y_arr, y_errors, x_label, y_label, filename, title=None, y_limits=None):
    outfile = open("{}/{}.txt".format(WORKING_DIR, filename), "w")
    print("# x y_lower y_avg y_upper", file=outfile)
    for i in range(len(x_arr)):
        print(f"{x_arr[i]} {y_arr[0][i]:.6f} {y_arr[1][i]:.6f} {y_arr[2][i]:.6f}", file=outfile)
    outfile.close()


pbs = [[] for _ in range(N_BLOBS)]
delays = [[] for _ in range(N_BLOBS)]
forwarding = [[] for _ in range(N_BLOBS)]
scheduling = [[] for _ in range(N_BLOBS)]
probing = [[] for _ in range(N_BLOBS)]
accepted = [[] for _ in range(N_BLOBS)]
rejected = [[] for _ in range(N_BLOBS)]

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
        probing[line_n].append(float(values[3]))
        scheduling[line_n].append(float(values[4]))
        forwarding[line_n].append(float(values[5]))
        accepted[line_n].append(float(values[6]))
        rejected[line_n].append(float(values[7]))
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

forwarding_avgs = []
forwarding_vars = []
forwarding_upper = []
forwarding_lower = []
forwarding_errors = []

probing_avgs = []
probing_vars = []
probing_upper = []
probing_lower = []
probing_errors = []

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


for i in range(N_BLOBS):
    print("> Computing values for pb, T=%d" % i)
    computeValues(i, pbs, pbs_avgs, pbs_vars, pbs_upper, pbs_lower, pbs_errors)
    print("> Computing values for delays, T=%d" % i)
    computeValues(i, delays, delays_avgs, delays_vars, delays_upper, delays_lower, delays_errors)
    print("> Computing values for forwarding, T=%d" % i)
    computeValues(i, forwarding, forwarding_avgs, forwarding_vars, forwarding_upper, forwarding_lower, forwarding_errors)
    print("> Computing values for probing, T=%d" % i)
    computeValues(i, probing, probing_avgs, probing_vars, probing_upper, probing_lower, probing_errors)
    print("> Computing values for accepted, T=%d" % i)
    computeValues(i, accepted, accepted_avgs, accepted_vars, accepted_upper, accepted_lower, accepted_errors)
    print("> Computing values for rejected, T=%d" % i)
    computeValues(i, rejected, rejected_avgs, rejected_vars, rejected_upper, rejected_lower, rejected_errors)

print("> Plotting pb")
TITLE = "6rpi - T=2 - 2000reqs - K=4"
X_AXIS = [str(int(BLOB_SIZES[i] / 1000)) for i in range(N_BLOBS)]

plot_confidence(X_AXIS, [pbs_lower, pbs_avgs, pbs_upper], pbs_errors,
                "Payload Size (kb)", "$P_B$", "pbs_confidence", TITLE)
save_confidence(X_AXIS, [pbs_lower, pbs_avgs, pbs_upper], pbs_errors,
                "Payload Size (kb)", "$P_B$", "pbs_confidence", TITLE)

print("> Plotting delays")
plot_confidence(X_AXIS, [delays_lower, delays_avgs, delays_upper], delays_errors,
                "Payload Size (kb)", "Delay (s)", "delay_confidence", TITLE)
save_confidence(X_AXIS, [delays_lower, delays_avgs, delays_upper], delays_errors,
                "Payload Size (kb)", "Delay (s)", "delay_confidence", TITLE)

print("> Plotting forwarding")
plot_confidence(X_AXIS, [forwarding_lower, forwarding_avgs, forwarding_upper], forwarding_errors,
                "Payload Size (kb)", "Forwarding Delay (s)", "forwarding_confidence", TITLE)
save_confidence(X_AXIS, [forwarding_lower, forwarding_avgs, forwarding_upper], forwarding_errors,
                "Payload Size (kb)", "Forwarding Delay (s)", "forwarding_confidence", TITLE)

print("> Plotting probing")
plot_confidence(X_AXIS, [probing_lower, probing_avgs, probing_upper], probing_errors,
                "Payload Size (kb)", "Probing Delay (s)", "probing_confidence", TITLE)
save_confidence(X_AXIS, [probing_lower, probing_avgs, probing_upper], probing_errors,
                "Payload Size (kb)", "Probing Delay (s)", "probing_confidence", TITLE)

print("> Plotting accepted")
plot_confidence(X_AXIS, [accepted_lower, accepted_avgs, accepted_upper], accepted_errors,
                "Payload Size (kb)", "Accepted Requests", "accepted_confidence", TITLE)
save_confidence(X_AXIS, [accepted_lower, accepted_avgs, accepted_upper], accepted_errors,
                "Payload Size (kb)", "Accepted Requests", "accepted_confidence", TITLE)

print("> Plotting rejected")
plot_confidence(X_AXIS, [rejected_lower, rejected_avgs, rejected_upper], rejected_errors,
                "Payload Size (kb)", "Rejected Requests", "rejected_confidence", TITLE)
save_confidence(X_AXIS, [rejected_lower, rejected_avgs, rejected_upper], rejected_errors,
                "Payload Size (kb)", "Rejected Requests", "rejected_confidence", TITLE)

# print pb with model
MODEL_DATA = ""  # "/home/gabrielepmattia/Coding/papers/paper-2020-unk-deadline/model-kolm/raw/20201028-154703-mswim_final_kolm_new_2_pb_log.txt"
if MODEL_DATA == "":
    exit(0)

data_file = open(MODEL_DATA, "r")
data_x = []
data_y = []
for line in data_file:
    values = line.split(" ")
    data_x.append(int(float(values[0]) * 1000))
    data_y.append(float(values[1]))

print(data_x)
print(data_y)

Plot.multi_plot([X_AXIS, data_x], [pbs_avgs, data_y], "Payload Size (kb)", "PB",
                "pbs_model_comparison", legend=["Experiment", "Model"], title=TITLE)
