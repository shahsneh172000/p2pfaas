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

import getopt
import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt

from model_mm1k import MM1K

# LaTex plot init
# USE_TEX = PlotUtils.use_tex()
USE_TEX = False

DICT_LAMBDA = "lambda"
DICT_PB = "pb"
DICT_DELAY = "timeDelay"
DICT_PE = "pe"
DICT_QUEUE_TIME = "timeQueue"
DICT_EXEC_TIME = "timeExec"
DICT_FAAS_EXEC_TIME = "timeFaasExec"
DICT_PROBE_TIME = "timeProbing"
DICT_FORWARDING_TIME = "timeForwarding"
DICT_PROBE_MESSAGES = "probeMessages"

DICT_PROBINGS_OVER_REQUESTS = "probingsOverRequests"

PLOT_MARKERS = ".,ov^<>x12348s"
PLOT_LINES = ['-', '--', '-.', ':']

labels = {
    DICT_LAMBDA: "λ" if not USE_TEX else r"$\lambda$",
    DICT_PB: "pb" if not USE_TEX else r"$P_B$",
    DICT_DELAY: "Delay (s)" if not USE_TEX else r"$W$ (s)",
    DICT_PE: "pe" if not USE_TEX else r"$P_E$",
    DICT_QUEUE_TIME: "Queue Time",
    DICT_EXEC_TIME: "Execution Time",
    DICT_FAAS_EXEC_TIME: "FaaS Execution Time",
    DICT_PROBE_TIME: "Probing Time (s)",
    DICT_FORWARDING_TIME: "Forwarding Time",
    DICT_PROBE_MESSAGES: "Probe Messages",

    DICT_PROBINGS_OVER_REQUESTS: "Probe Messages per Request"
}


def getBaseDict():
    features = getFeaturesArray()
    d = {DICT_LAMBDA: []}
    for f in features:
        d[f] = []
    return d


def getFeaturesArray():
    return [DICT_PB,
            DICT_DELAY,
            DICT_PE,
            DICT_QUEUE_TIME,
            DICT_EXEC_TIME,
            DICT_FAAS_EXEC_TIME,
            DICT_PROBE_TIME,
            DICT_FORWARDING_TIME,
            DICT_PROBE_MESSAGES]


def parseResultFile(file_path):
    # check if file exists
    mfile = Path(file_path)
    if not mfile.is_file():
        print("> file %s does not exist" % file_path)
        return {}

    in_file = open(file_path, "r")
    d = getBaseDict()

    for line in in_file:
        if line[0] == "#":
            continue
        comps = line.split()
        d[DICT_LAMBDA].append(float(comps[0]))
        d[DICT_PB].append(float(comps[1]))
        d[DICT_DELAY].append(float(comps[2]))
        d[DICT_PE].append(float(comps[3]))
        if len(comps) >= 9:
            d[DICT_QUEUE_TIME].append(float(comps[4]))
            d[DICT_EXEC_TIME].append(float(comps[5]))
            d[DICT_FAAS_EXEC_TIME].append(float(comps[6]))
            d[DICT_PROBE_TIME].append(float(comps[7]))
            d[DICT_FORWARDING_TIME].append(float(comps[8]))
            d[DICT_PROBE_MESSAGES].append(float(comps[9]))

    in_file.close()
    return d


def parseAllResultFiles(path, from_t, to_t, m, k, function):
    d_all = {}
    for t in range(from_t, to_t + 1):
        filename = "{}-avg-k{}-t{}-m{}.txt".format(
            function.lower().replace(" ", ""), k, t, m)
        print("> Parsing file \"%s\"" % filename)
        d_t = parseResultFile("{}/{}".format(path, filename))
        d_all[t] = d_t
    return d_all


def plotFeaturesComparison(d_all, from_t, to_t, m, k, function, mi, f, from_l, to_l, l_delta, out_plots_dir):
    lambdas = int((to_l - from_l) / l_delta) + 1

    def plotData(x_plot, y_plots, y_labels, feature):
        title = "{} - LL({},T) - (K={}, μ={:.2f}) - {}machines".format(function, f, k, mi, m)
        filename = "comparison-{}.pdf".format(feature)
        print("> Plotting \"%s\"" % filename)

        plt.cla()
        plt.clf()
        plt.close()
        fig, ax = plt.subplots()

        i = 0
        for arr in y_plots:
            ax.plot(x_plot, arr, marker="x",
                    markersize=3.0, markeredgewidth=1, linewidth=0.7, label="T = {}".format(y_labels[i]))
            i += 1

        ax.set_xlabel(labels[DICT_LAMBDA])
        ax.set_ylabel(labels[feature])
        ax.set_title(title)
        ax.legend()
        fig.tight_layout()
        plt.savefig("{}/{}".format(out_plots_dir, filename))

    def retrieveData(feature):
        x_plot = []
        y_plots = []
        y_labels = []
        for t in range(from_t, to_t + 1):
            if feature in d_all[t].keys():
                y_plots.append(d_all[t][feature])
                y_labels.append(t)
                if len(x_plot) == 0:
                    x_plot = d_all[t][DICT_LAMBDA]
        return (x_plot, y_plots, y_labels)

    features = getFeaturesArray()
    for feature in features:
        x, y, y_labels = retrieveData(feature)
        plotData(x, y, y_labels, feature)


def plotFixedLambdaFeatures(d_all, from_t, to_t, m, k, function, mi, from_l, to_l, l_delta, f, out_plots_dir):
    lambdas = int((to_l - from_l) / l_delta) + 1

    def getLAtIndex(i):
        return l_delta * i + from_l

    def getLiFromV(l):
        return int(round(((l - from_l) / l_delta)))

    def plotData(to_plot_x, to_plot_y, l, feature):
        title = "{} - LL({},T) - (K={}, μ={:.2f}) - {}machines - λ = {:.2f}".format(function, f, k, mi, m, l)
        filename = "{}-fixedl{}.pdf".format(feature, "{:.2f}".format(l).replace(".", "_"))
        print("> Plotting \"%s\"" % filename)

        plt.cla()
        plt.clf()
        plt.close()
        fig, ax = plt.subplots()

        ax.plot(to_plot_x, to_plot_y, marker=markers[0], markersize=4.0,
                markeredgewidth=0.4, linewidth=0.7, label="λ = {:.2f}".format(l))

        # add model
        model_values = []
        if feature == DICT_PB:
            for t in range(from_t, to_t + 1):
                model_values.append(MM1K.P_B(l, mi, k))
        elif feature == DICT_DELAY:
            for t in range(from_t, to_t + 1):
                model_values.append(MM1K.delay(l, mi, k))
        if len(model_values) > 0:
            ax.plot(to_plot_x, model_values, marker=markers[1], markersize=4.0,
                    markeredgewidth=0.4, linewidth=0.7, label="M/M/1/K Model")

        ax.set_xlabel("T")
        ax.set_ylabel(labels[feature])
        ax.set_title(title)
        # ax.legend()
        fig.tight_layout()
        plt.savefig("{}/{}".format(out_plots_dir, filename))

    def plotAllData(x_plot, y_plots, y_labels, feature, select=False):
        title = "{} - LL({},T) - (K={}, μ={:.2f}) - {}machines".format(function, f, k, mi, m)
        filename = "allData-{}.pdf".format(feature)
        if select:
            filename = "allData-selection-{}.pdf".format(feature)
        print("> Plotting \"%s\"" % filename)

        plt.cla()
        plt.clf()
        plt.close()
        fig, ax = plt.subplots()

        i = 0
        for arr in y_plots:
            ax.plot(x_plot, arr, marker="x", markersize=3.0, markeredgewidth=1, linewidth=0.7, label=y_labels[i])
            i += 1

        ax.set_xlabel("T")
        ax.set_ylabel(labels[feature])
        ax.set_title(title)
        if select:
            ax.legend()
        fig.tight_layout()
        plt.savefig("{}/{}".format(out_plots_dir, filename))

    def retrievePlotData(l_index, feature):
        to_plot_y = []
        to_plot_x = []

        for t in range(from_t, to_t + 1):
            to_plot_x.append(t)
            if feature not in d_all[t].keys():
                to_plot_y.append(0)
            else:
                to_plot_y.append(d_all[t][feature][l_index])
        return (to_plot_x, to_plot_y)

    def retrieveAllData(feature, select=None):
        x_plot = []
        y_plots = []
        y_labels = []

        for l_index in range(lambdas):
            if select != None and l_index not in select:
                continue
            x, y = retrievePlotData(l_index, feature)
            y_plots.append(y)
            y_labels.append("λ = {:.2f}".format(getLAtIndex(l_index)))
            if len(x_plot) == 0:
                x_plot = x

        return (x_plot, y_plots, y_labels)

    for l_index in range(lambdas):
        l_value = getLAtIndex(l_index)
        x, y = retrievePlotData(l_index, DICT_PB)
        plotData(x, y, l_value, DICT_PB)
        x, y = retrievePlotData(l_index, DICT_DELAY)
        plotData(x, y, l_value, DICT_DELAY)
        x, y = retrievePlotData(l_index, DICT_PE)
        plotData(x, y, l_value, DICT_PE)
        x, y = retrievePlotData(l_index, DICT_PROBE_MESSAGES)
        plotData(x, y, l_value, DICT_PROBE_MESSAGES)
        x, y = retrievePlotData(l_index, DICT_PROBE_TIME)
        plotData(x, y, l_value, DICT_PROBE_TIME)
        # prepare probings over requests
        x, y = retrievePlotData(l_index, DICT_PROBE_MESSAGES)
        x_e, y_e = retrievePlotData(l_index, DICT_PE)
        # print(y)
        # print(y_e)
        # y = list(map(lambda v: (v * 2) / 20000, y))
        # for i in range(len(y)):
        #     forwarded = y_e[i] * 20000
        #     y[i] = ((y[i] + forwarded) * 2) / 20000
        # print(y)
        # plotData(x, y, l_value, DICT_PROBINGS_OVER_REQUESTS)

    select = [getLiFromV(3.00), getLiFromV(3.30), getLiFromV(3.50), getLiFromV(3.60)]
    x, y, l = retrieveAllData(DICT_PB, select=select)
    plotAllData(x, y, l, DICT_PB, select=True)
    x, y, l = retrieveAllData(DICT_DELAY, select=select)
    plotAllData(x, y, l, DICT_DELAY, select=True)
    # plot all data
    x, y, l = retrieveAllData(DICT_PB)
    plotAllData(x, y, l, DICT_PB)
    x, y, l = retrieveAllData(DICT_DELAY)
    plotAllData(x, y, l, DICT_DELAY)


def start_plot(path, function, f, from_t, to_t, mi, from_l, to_l, l_delta, k, m, out_plots_dir):
    d_all = parseAllResultFiles(path, from_t, to_t, m, k, function)
    plotFixedLambdaFeatures(d_all, from_t, to_t, m, k, function, mi, from_l, to_l, l_delta, f, out_plots_dir)
    plotFeaturesComparison(d_all, from_t, to_t, m, k, function, mi, f, from_l, to_l, l_delta, out_plots_dir)


def main(argv):
    path = ""
    function = ""
    fanout = 1
    from_t = 1
    to_t = 10
    job_duration = 1.0
    start_lambda = 0.1
    end_lambda = 1.0
    lambda_delta = 0.05
    k = 10
    m = 8

    usage = "plot_times.py"
    try:
        opts, args = getopt.getopt(
            argv, "hk:p:",
            ["path=", "function=", "fanout=", "from-threshold=", "to-threshold=", "job-duration=", "start-lambda=",
             "end-lambda=", "lambda-delta=", "n-machines="])
    except getopt.GetoptError:
        print(usage)
        sys.exit(2)
    for opt, arg in opts:
        # print(opt + " -> " + arg)
        if opt == '-h':
            print(usage)
            sys.exit()
        elif opt in ("-p", "--path"):
            path = arg
        elif opt in "-k":
            k = int(arg)
        elif opt in "--n-machines":
            m = int(arg)
        elif opt in "--function":
            function = arg
        elif opt in "--fanout":
            fanout = int(arg)
        elif opt in "--from-threshold":
            from_t = int(arg)
        elif opt in "--to-threshold":
            to_t = int(arg)
        elif opt in "--job-duration":
            job_duration = float(arg)
        elif opt in "--start-lambda":
            start_lambda = float(arg)
        elif opt in "--end-lambda":
            end_lambda = float(arg)
        elif opt in "--lambda-delta":
            lambda_delta = float(arg)

    if path == "":
        print("Some needed parameter was not given")
        print(usage)
        sys.exit()

    out_plots_dir = "{0}/{1}".format(path, "_plots")
    os.makedirs(out_plots_dir, exist_ok=True)

    print("====== P2P-FOG Plot Utilities ======")
    print("> path %s" % path)
    print("> function %s" % function)
    print("> fanout %d" % fanout)
    print("> from_t %d" % from_t)
    print("> to_t %d" % to_t)
    print("> k %d" % k)
    print("> job_duration %f" % job_duration)
    print("> start_lambda %.2f" % start_lambda)
    print("> end_lambda %.2f" % end_lambda)
    print("> lambda_delta %.2f" % lambda_delta)
    print("> m %d" % m)
    print("----")
    print("> out_plots_dir %s" % out_plots_dir)
    print("")

    mi = 1.0 / job_duration

    start_plot(path, function, fanout, from_t, to_t, mi, start_lambda, end_lambda, lambda_delta, k, m, out_plots_dir)


if __name__ == "__main__":
    main(sys.argv[1:])
