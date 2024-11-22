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

from plot.utils import Plot, PlotUtils

BASE_DIR = "/Users/gabrielepmattia/Coding/p2p-faas/experiments-data/BladeServers/PigoFaceDetectF/"

TEST_FOLDER1 = BASE_DIR + "LL-PS(1,K)/10000reqs-T8/_bench_multi_machine-12072019-122813/"
TEST_FOLDER2 = BASE_DIR + "RR(K=10)/_bench_multi_machine-12082019-110545"

LEGEND_1 = "PWR(1,8)"
LEGEND_2 = "RR"

N_MACHINES = 8

##
DICT_TAG_LAMBDA = "LAMBDA"
DICT_TAG_PB = "PB"
DICT_TAG_PE = "PE"
DICT_TAG_REQUEST_TIME = "REQUEST_TIME"
DICT_TAG_EXEC_TIME = "EXEC_TIME"
DICT_TAG_FORWARD_TIME = "FORWARD_TIME"
DICT_TAG_SCHEDULING_TIME = "SCHEDULING_TIME"
DICT_TAG_SCHEDULING_EX_TIME = "SCHEDULING_EX_TIME"

FEATURES = [DICT_TAG_PB, DICT_TAG_PE, DICT_TAG_REQUEST_TIME, DICT_TAG_EXEC_TIME, DICT_TAG_FORWARD_TIME,
            DICT_TAG_SCHEDULING_TIME, DICT_TAG_SCHEDULING_EX_TIME]


def get_base_dict():
    return {
        DICT_TAG_LAMBDA: [],
        DICT_TAG_PB: [],
        DICT_TAG_PE: [],
        DICT_TAG_REQUEST_TIME: [],
        DICT_TAG_EXEC_TIME: [],
        DICT_TAG_FORWARD_TIME: [],
        DICT_TAG_SCHEDULING_TIME: [],
        DICT_TAG_SCHEDULING_EX_TIME: []
    }


def parse_avg_dict(dir):
    dicts = []
    for i in range(N_MACHINES):
        dicts.append(get_base_dict())
        values_file = open("{}/results-machine-{:02d}.txt".format(dir, i), "r")
        for line in values_file:
            cmps = line.split(" ")
            dicts[i][DICT_TAG_LAMBDA].append(cmps[0])
            dicts[i][DICT_TAG_PB].append(round(float(cmps[1]), 5))
            dicts[i][DICT_TAG_PE].append(round(float(cmps[2]), 5))
            dicts[i][DICT_TAG_REQUEST_TIME].append(round(float(cmps[3]), 5))
            dicts[i][DICT_TAG_EXEC_TIME].append(round(float(cmps[4]), 5))
            dicts[i][DICT_TAG_FORWARD_TIME].append(round(float(cmps[5]), 5))
            dicts[i][DICT_TAG_SCHEDULING_TIME].append(round(float(cmps[6]), 5))
            dicts[i][DICT_TAG_SCHEDULING_EX_TIME].append(round(float(cmps[7]), 5))

    # compute the average dict

    def compute_avg_feature(dicts, feature, i):
        total = 0.0
        for dict in dicts:
            total += dict[feature][i]
        return total / len(dicts)

    out_dict = get_base_dict()
    out_dict[DICT_TAG_LAMBDA] = dicts[0][DICT_TAG_LAMBDA]
    for f in FEATURES:
        for i in range(len(dicts[0][DICT_TAG_LAMBDA])):
            out_dict[f].append(compute_avg_feature(dicts, f, i))

    return out_dict


avg1 = parse_avg_dict(TEST_FOLDER1)
avg2 = parse_avg_dict(TEST_FOLDER2)

legend = ["PWR-N(1,8)", "RR"]
CHART_TITLE = "PigoFaceDetectF - K=10 - mi=" + str(round(1.0 / 0.28, 2))

# plot
x_arrs = [avg1[DICT_TAG_LAMBDA], avg2[DICT_TAG_LAMBDA]]
y_arrs_pb = [avg1[DICT_TAG_PB], avg2[DICT_TAG_PB]]
y_arrs_pe = [avg1[DICT_TAG_PE], avg2[DICT_TAG_PE]]
y_arrs_delay = [avg1[DICT_TAG_REQUEST_TIME], avg2[DICT_TAG_REQUEST_TIME]]
y_arrs_exec = [avg1[DICT_TAG_EXEC_TIME], avg2[DICT_TAG_EXEC_TIME]]
y_arrs_forwarding = [avg1[DICT_TAG_FORWARD_TIME], avg2[DICT_TAG_FORWARD_TIME]]
y_arrs_sched = [avg1[DICT_TAG_SCHEDULING_TIME], avg2[DICT_TAG_SCHEDULING_TIME]]
y_arrs_sched_ex = [avg1[DICT_TAG_SCHEDULING_EX_TIME], avg2[DICT_TAG_SCHEDULING_EX_TIME]]

PlotUtils.use_tex()
Plot.multi_plot(x_arrs, y_arrs_pb, "lambda", "pb", "pb_comparison", legend=legend, title=CHART_TITLE)
Plot.multi_plot(x_arrs, y_arrs_pe, "lambda", "pe", "pe_comparison", legend=legend, title=CHART_TITLE)
Plot.multi_plot(x_arrs, y_arrs_delay, "lambda", "s", "time_req_comparison", legend=legend, title=CHART_TITLE)
Plot.multi_plot(x_arrs, y_arrs_exec, "lambda", "s", "time_exec_comparison", legend=legend, title=CHART_TITLE)
Plot.multi_plot(x_arrs, y_arrs_forwarding, "lambda", "s", "time_frwd_comparison", legend=legend, title=CHART_TITLE)
Plot.multi_plot(x_arrs, y_arrs_sched, "lambda", "s", "time_sched_comparison", legend=legend, title=CHART_TITLE)
Plot.multi_plot(x_arrs, y_arrs_sched_ex, "lambda", "s", "time_sched_ex_comparison", legend=legend, title=CHART_TITLE)
