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

import sys
import getopt
import os
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

labels = {
    DICT_LAMBDA: "λ" if not USE_TEX else r"$\lambda$",
    DICT_PB: "pb" if not USE_TEX else r"$P_B$",
    DICT_DELAY: "Delay (s)" if not USE_TEX else r"$W$ (s)",
    DICT_PE: "pe",
    DICT_QUEUE_TIME: "Queue Delay (s)",
    DICT_EXEC_TIME: "Exec Delay (s)",
    DICT_FAAS_EXEC_TIME: "OpenFaaS Exec Delay (s)",
    DICT_PROBE_TIME: "Probing Delay (s)",
    DICT_FORWARDING_TIME: "Forwarding Delay (s)",
    DICT_PROBE_MESSAGES: "probeMessages",

    DICT_PROBINGS_OVER_REQUESTS: "Probe Messages per Request"
}


def get_base_dict():
    features = get_features_array()
    d = {DICT_LAMBDA: []}
    for f in features:
        d[f] = []
    return d


def get_features_array():
    return [DICT_PB,
            DICT_DELAY,
            DICT_PE,
            DICT_QUEUE_TIME,
            DICT_EXEC_TIME,
            DICT_FAAS_EXEC_TIME,
            DICT_PROBE_TIME,
            DICT_FORWARDING_TIME,
            DICT_PROBE_MESSAGES]


def get_features_to_print_array():
    return [DICT_PB,
            DICT_DELAY,
            DICT_PE,
            DICT_QUEUE_TIME,
            DICT_EXEC_TIME,
            DICT_FAAS_EXEC_TIME,
            DICT_PROBE_TIME,
            DICT_FORWARDING_TIME,
            DICT_PROBE_MESSAGES,
            DICT_PROBINGS_OVER_REQUESTS]


def print_dict(d, outfile):
    features = get_features_to_print_array()
    features_t = ("lambda", "pB", "MeanReqTime", "pE", "MeanQueueTime",
                  "MeanExecTime", "MeanFaasExecTime", "MeanProbeTime", "MeanForwardingTime", "ProbeMessages",
                  "ProbesOverRequests")
    print("# %s %s %s %s %s %s %s %s %s %s %s" % features_t, file=outfile)
    for i in range(len(d[DICT_LAMBDA])):
        print("%.2f" % d[DICT_LAMBDA][i], end="", file=outfile)
        for f in features:
            if len(d[f]) == 0:
                print(" %.6f" % 0.0, end="", file=outfile)
                continue
            print(" %.6f" % d[f][i], end="", file=outfile)
        print("\n", end="", file=outfile)


def parse_log_file(file_path):
    in_file = open(file_path, "r")
    d = get_base_dict()

    for line in in_file:
        if line[0] == "#" or line.strip() == "":
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
            d[DICT_PROBE_MESSAGES].append(int(comps[9]))

    in_file.close()
    return d


def start_plot(files_path, files_prefix, files_number, out_dir, k, f, t, mi, function, with_model, model_name,
               plot_every_machine, algorithm):
    function_normalized = function.lower().replace(" ", "")

    def plotData(d, feature, title, filename, model=None):
        if len(d[feature]) == 0:
            return

        plt.clf()
        fig, ax = plt.subplots()
        line_experimental, = ax.plot(d[DICT_LAMBDA], d[feature], marker="x",
                                     markersize=3.0, markeredgewidth=1, linewidth=0.7)
        if model != None:
            lines_model, = ax.plot(d[DICT_LAMBDA], model,
                                   markersize=4.0, markeredgewidth=0.3, linewidth=1.2)
            plt.legend([line_experimental, lines_model], ['Experiment', "Model " + model_name])

        ax.set_title(title)
        ax.set_xlabel(labels[DICT_LAMBDA])
        ax.set_ylabel(labels[feature])
        fig.tight_layout()
        plt.savefig("{}/{}".format(out_dir, filename))
        plt.close(fig)

    def plotFeatures(d, title):
        features = get_features_array()
        for f in features:
            filename = "{}-avg-{}-k{}.pdf".format(function_normalized, f, k)
            print("Plotting %s to \"%s\"" % (f, filename))

            if f == DICT_PB and with_model:
                plotData(d, f, title, filename, MM1K.generatePbArray(d[DICT_LAMBDA], k, mi))
            elif f == DICT_DELAY and with_model:
                plotData(d, f, title, filename, MM1K.generateDelayArray(d[DICT_LAMBDA], k, mi))
            else:
                plotData(d, f, title, filename)

    def plotAverage(dicts):
        chart_title = ""
        if algorithm == "NS(K)":
            chart_title = "{} - NS({}) - (μ={:.4f})".format(function, k, mi)
        elif algorithm == "LL-PS(F,T)":
            chart_title = "{} - LL({}, K-{}) - (K={},μ={:.4f}) - Average of {}".format(function,
                                                                                       f, t, k, mi, files_number)
        elif algorithm == "RR(K)":
            chart_title = "{0} - RR(K) - (K={1},μ={2:.4f}) - Average of {3}".format(function, k, mi, files_number)

        d = mean_dict(dicts)
        plotFeatures(d, chart_title)

        stacked_filename = "{}-avg-timingsStacked-k{}.pdf".format(function_normalized, k)
        print("Plotting %s to \"%s\"" % (stacked_filename, stacked_filename))
        plotStackedTimings(d, chart_title, stacked_filename)

    def plotDataForMachine(i, d, feature, model=None):
        chart_title = ""
        if algorithm == "NS(K)":
            chart_title = "{0} - NS({1}) - (μ={2:.4f}) - Machine{3}".format(function, k, mi, i)
        elif algorithm == "LL-PS(F,T)":
            chart_title = "{0} - LL({1}, K-{2}) - (K={3},μ={4:.4f}) - Machine{5}".format(function, f, t, k, mi, i)
        elif algorithm == "RR(K)":
            chart_title = "{0} - RR(K) - (K={1},μ={2:.4f}) - Machine{3}".format(function, k, mi, i)

        filename = "{}-machine{:02}-k{}.pdf".format(feature, i, k)
        print("[MACHINE#%02d] Plotting %s to \"%s-machine%02d-k%d\"" % (i, feature, feature, i, k))
        plotData(d, feature, chart_title, filename, model)

    def plotFeaturesForMachine(i, d):
        features = get_features_array()
        for f in features:
            if f == DICT_PB and with_model:
                plotDataForMachine(i, d, f, MM1K.generatePbArray(d[DICT_LAMBDA], k, mi))
            elif f == DICT_DELAY and with_model:
                plotDataForMachine(i, d, f, MM1K.generateDelayArray(d[DICT_LAMBDA], k, mi))
            else:
                plotDataForMachine(i, d, f)

    def plotStackedTimings(d, title, filename):
        for f in get_features_array():
            if len(d[f]) == 0:
                return

        plt.clf()
        fig, ax = plt.subplots()
        ax.set_title(title)
        ax.set_xlabel(labels[DICT_LAMBDA])
        ax.set_ylabel("Delay (s)")
        y00 = [0] * len(d[DICT_LAMBDA])
        y0 = d[DICT_PROBE_TIME]
        y1 = sumArrays(y0, d[DICT_FORWARDING_TIME])
        y2 = sumArrays(y1, d[DICT_FAAS_EXEC_TIME])
        y3 = sumArrays(y2, diffArrays(d[DICT_EXEC_TIME], d[DICT_FAAS_EXEC_TIME]))
        # y9 = d[DICT_DELAY]
        y0p, = ax.plot(d[DICT_LAMBDA], y0, linewidth=0.5)
        y1p, = ax.plot(d[DICT_LAMBDA], y1, linewidth=0.5)
        y2p, = ax.plot(d[DICT_LAMBDA], y2, linewidth=0.5)
        y3p, = ax.plot(d[DICT_LAMBDA], y3, linewidth=0.5)
        # y9p, = ax.plot(d[DICT_LAMBDA], y9, linewidth=0.5)
        ax.legend([y0p, y1p, y2p, y3p], [labels[DICT_PROBE_TIME], labels[DICT_FORWARDING_TIME],
                                         labels[DICT_FAAS_EXEC_TIME], labels[DICT_EXEC_TIME]])
        ax.fill_between(d[DICT_LAMBDA], y0, y00, where=y0 >= y00, facecolor='C0', alpha=0.2)
        ax.fill_between(d[DICT_LAMBDA], y1, y0, where=y1 >= y0, facecolor='C1', alpha=0.2)
        ax.fill_between(d[DICT_LAMBDA], y2, y1, where=y1 >= y0, facecolor='C2', alpha=0.2)
        ax.fill_between(d[DICT_LAMBDA], y3, y2, where=y3 >= y3, facecolor='C3', alpha=0.2)
        # ax.fill_between(d[DICT_LAMBDA], y9, y3, where=y9 >= y3, facecolor='C4', alpha=0.2)
        fig.tight_layout()
        plt.savefig("{}/{}".format(out_dir, filename))
        plt.close(fig)

    def plotStackedTimingsForMachine(i, d):
        filetitle = "timeStacked"
        filename = "{}-machine{:02}-k{}.pdf".format(filetitle, i, k)
        title = "{0} - LL({1}, K-{2}) - (K={3},μ={4:.4f}) - Machine{5}".format(function, f, t, k, mi, i)
        print("[MACHINE#%02d] Plotting %s to \"%s\"" % (i, filetitle, filetitle))
        plotStackedTimings(d, title, filename)
        # create plot dirs

    os.makedirs(out_dir, exist_ok=True)
    dicts = []
    for i in range(files_number):
        d = parse_log_file("{0}/{1}{2:02}.txt".format(files_path, files_prefix, i))
        dicts.append(d)

        if plot_every_machine:
            plotFeaturesForMachine(i, d)
            plotStackedTimingsForMachine(i, d)
    plotAverage(dicts)


def do_computations(files_path, files_prefix, files_number, out_dir, k, f, t, mi, function, with_model, model_name):
    averages_filename = "{}-avg-k{}-t{}-m{}.txt".format(function.lower().replace(" ", ""), k, t, files_number)

    def saveAverages(d):
        outfile = open("{}/{}".format(out_dir, averages_filename), "w")
        print_dict(d, outfile)
        outfile.close()

    os.makedirs(out_dir, exist_ok=True)
    dicts = []
    for i in range(files_number):
        d = parse_log_file("{0}/{1}{2:02}.txt".format(files_path, files_prefix, i))
        dicts.append(d)

    d = mean_dict(dicts)
    saveAverages(d)

    #
    # Utils
    #


def sumArrays(array1, array2):
    out = []
    if len(array1) != len(array2):
        return out
    for i in range(len(array1)):
        out.append(array1[i] + array2[i])
    return out


def diffArrays(array1, array2):
    out = []
    if len(array1) != len(array2):
        return out
    for i in range(len(array1)):
        out.append(array1[i] - array2[i])
    return out


def mean_dict(dicts):
    """Computer the average dict of an array of dicts passed"""
    avg_dict = get_base_dict()
    features = get_features_array()
    n = len(dicts)
    print("Computing mean dict of %d dicts" % n)
    for f in features:
        for i in range(len(dicts[0][f])):
            summation = 0.0
            for d in dicts:
                summation += d[f][i]
            avg_dict[f].append(summation / float(n))
    # copy lambda
    for l in dicts[0][DICT_LAMBDA]:
        avg_dict[DICT_LAMBDA].append(l)

    # add probing messages per requests
    avg_dict[DICT_PROBINGS_OVER_REQUESTS] = []
    for i in range(len(dicts[0][DICT_PE])):
        avg_dict[DICT_PROBINGS_OVER_REQUESTS].append(avg_dict[DICT_PROBE_MESSAGES][i] + avg_dict[DICT_PE][i] * 20000)

    return avg_dict


#
# Entrypoint
#


def main(argv):
    files_path = ""
    files_prefix = "res-line-"
    files_number = 1
    function = ""
    fanout = 1
    threshold = 1
    job_duration = 1
    k = 10
    with_model = False
    model_name = ""
    plot_every_machine = False
    algorithm = ""

    usage = "plot_times.py"
    try:
        opts, args = getopt.getopt(
            argv, "hk:p:",
            ["files-prefix=", "files-n=", "path=", "function=", "fanout=", "threshold=", "job-duration=", "with-model",
             "model-name=", "plot-every-machine", "algorithm="])
    except getopt.GetoptError:
        print(usage)
        sys.exit(2)
    for opt, arg in opts:
        # print(opt + " -> " + arg)
        if opt == '-h':
            print(usage)
            sys.exit()
        elif opt in ("-p", "--path"):
            files_path = arg
        elif opt in "--files-prefix":
            files_prefix = arg
        elif opt in "--function":
            function = arg
        elif opt in "--files-n":
            files_number = int(arg)
        elif opt in "--fanout":
            fanout = int(arg)
        elif opt in "--threshold":
            threshold = int(arg)
        elif opt in "--job-duration":
            job_duration = float(arg)
        elif opt in "-k":
            k = int(arg)
        elif opt in "--with-model":
            with_model = True
        elif opt in "--model-name":
            model_name = arg
        elif opt in "--plot-every-machine":
            plot_every_machine = True
        elif opt in "--algorithm":
            algorithm = arg

    out_plots_dir = "{0}/{1}".format(files_path, "_plots")
    out_computations_dir = "{0}/{1}".format(files_path, "_computed")

    print("====== P2P-FOG Plot Utilities ======")
    print("> files_path %s" % files_path)
    print("> files_prefix %s" % files_prefix)
    print("> files_number %d" % files_number)
    print("> job_duration %f => mi %f" % (job_duration, 1.0 / job_duration))
    print("> k %d" % k)
    print("> with model %s" % with_model)
    print("> model name %s" % model_name)
    print("> plot_every_machine %s" % plot_every_machine)
    print("> algorithm %s" % algorithm)
    print("----")
    print("> out_plots_dir %s" % out_plots_dir)
    print("> out_computations_dir %s" % out_computations_dir)
    print("")

    if files_path == "":
        print("Some needed parameter was not given")
        print(usage)
        sys.exit()

    if not (algorithm == "NS(K)" or algorithm == "LL-PS(F,T)" or algorithm == "RR(K)"):
        print("Given algorithm is not supported")
        print(usage)
        sys.exit()

    for i in range(files_number):
        mfile = Path("{0}/{1}{2:02}.txt".format(files_path, files_prefix, i))
        if not mfile.is_file():
            print("File {0}/{1}{2:02}.txt does not exist".format(files_path, files_prefix, i))
            sys.exit()

    mi = 1.0 / job_duration
    start_plot(files_path, files_prefix, files_number, out_plots_dir, k,
               fanout, threshold, mi, function, with_model, model_name, plot_every_machine, algorithm)
    # startSuite(cmd_lines, start_lambda, end_lambda, lambda_delta)
    do_computations(files_path, files_prefix, files_number, out_computations_dir, k, fanout, threshold, mi,
                    function, with_model, model_name)


if __name__ == "__main__":
    main(sys.argv[1:])
