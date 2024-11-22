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

import sys
import getopt
import os
import matplotlib.pyplot as plt
import numpy as np

# LaTex plot init
# USE_TEX = PlotUtils.use_tex()
USE_TEX = False

def parseAllFiles(path, prefix, start_lambda, end_lambda, lambda_delta, k, machine_id):
    d = {}
    all_values = []

    current_lambda = start_lambda
    while True:
        d[str(current_lambda)] = []
        infile = open("{}/{}l{}-machine{:02}.txt".format(path, prefix,
                                                         str(round(current_lambda, 3)).replace(".", "_"), machine_id))
        for line in infile:
            if line[0] == "#":
                continue
            all_values.append(float(line))
            d[str(current_lambda)].append(float(line))

        infile.close()
        current_lambda = round(lambda_delta + current_lambda, 2)
        if current_lambda > end_lambda:
            break

    print("[DEBUG] Parsed %d lambdas" % len(d))
    return d, all_values


def parseFilesList(data_files, prefix, start_lambda, end_lambda, lambda_delta, k, machine_id):
    all_values = []
    for path in data_files:
        d, values = parseAllFiles(path, prefix, start_lambda, end_lambda, lambda_delta, k, machine_id)
        all_values += values
    return all_values


def start_plot(function, path, prefix, start_lambda, end_lambda, lambda_delta, f, t, k, mi, machine_id, bins,
               data_files):
    out_plots_dir = "{0}/{1}".format(path, "_plots_distribution")
    plot_title = "{} - LL({}, K-{}) - (K={},μ={:.4f}) - Machine#{}".format(function,
                                                                           f, t, k, mi, machine_id)
    function_normalized = function.lower().replace(" ", "")

    os.makedirs(out_plots_dir, exist_ok=True)
    d, all_values = parseAllFiles(path, prefix, start_lambda, end_lambda, lambda_delta, k, machine_id)
    if len(data_files) == 0:
        min_v = min(all_values)
        max_v = max(all_values)
    else:
        base_values = parseFilesList(data_files, prefix, start_lambda, end_lambda, lambda_delta, k, machine_id)
        min_v = min(base_values)
        max_v = max(base_values)

    def plotCumulativeFrequency():
        filename = "{}-all-values-cumulative-machine{:02}.pdf".format(function_normalized, machine_id)
        print("Plotting %s" % filename)
        histogram_binned, bins_edges = np.histogram(all_values, bins=bins, range=(min_v, max_v))

        histogram_data = []
        cumulative_occ = 0
        for i in range(len(histogram_binned)):
            cumulative_occ += histogram_binned[i]
            histogram_data.append(cumulative_occ)

        plt.clf()
        fig, ax = plt.subplots()
        ax.plot(bins_edges[1:], histogram_data, marker="x", markersize=3.0, markeredgewidth=1.0, linewidth=0.8)
        ax.set_xlabel("Delay (s)")
        ax.set_ylabel("Occurrences")
        ax.set_title(plot_title)
        fig.tight_layout()
        plt.savefig("{}/{}{}".format(out_plots_dir, "" if len(data_files) == 0 else "merged-", filename))

    def plotAllValuesHist():
        filename = "{}-all-values-hist-machine{:02}.pdf".format(function_normalized, machine_id)
        print("Plotting %s" % filename)
        plt.clf()
        plt.hist(all_values, bins=bins, range=(min_v, max_v))
        plt.xlabel("Delay (s)")
        plt.ylabel("Occurrences")
        plt.title(plot_title)
        plt.savefig("{}/{}{}".format(out_plots_dir, "" if len(data_files) == 0 else "merged-", filename))

    def plotHeatMap():
        filename = "{}-heatmap-hist-machine{:02}.pdf".format(function_normalized, machine_id)
        print("Plotting %s" % filename)
        plt.clf()
        bins_edges = []
        heat_matrix = []

        x_ticks = []
        y_ticks = []

        l = start_lambda
        while True:
            x_ticks.append(str(l))
            histogram_data, bins_edges = np.histogram(d[str(l)], bins=bins, range=(min_v, max_v))
            heat_matrix.append(histogram_data.tolist()[:: -1])
            l = round(lambda_delta + l, 2)
            if l > end_lambda:
                break
        # generate y_ticks
        for i in range(len(bins_edges)):
            if i + 1 >= len(bins_edges):
                break
            y_ticks.append("[{}, {}]".format(str(round(bins_edges[i], 2)), str(round(bins_edges[i + 1], 2))))
        y_ticks = y_ticks[:: -1]

        fig, ax = plt.subplots()
        im = ax.imshow(np.array(matrixSym(heat_matrix)))
        # colorbar
        cbar = ax.figure.colorbar(im, ax=ax)
        cbar.ax.set_ylabel("Occurrences", rotation=-90, va="bottom")
        # set ticks
        ax.set_xticks(np.arange(len(x_ticks)))
        ax.set_yticks(np.arange(len(y_ticks)))
        ax.set_xticklabels(x_ticks, fontsize="xx-small")
        ax.set_yticklabels(y_ticks, fontsize="x-small")
        ax.set_xlabel('λ')
        ax.set_ylabel('Delay (s)')
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
        # save
        plt.title(plot_title)
        fig.tight_layout()
        plt.savefig("{}/{}{}".format(out_plots_dir, "" if len(data_files) == 0 else "merged-", filename))

    plotAllValuesHist()
    plotHeatMap()
    plotCumulativeFrequency()


def matrixSym(m):
    out = [None] * len(m[0])
    for i in range(len(m[0])):
        out[i] = [0.0] * len(m)

    for i in range(len(m)):
        for j in range(len(m[i])):
            out[j][i] = m[i][j]
    return out


#
# Entrypoint
#


def main(argv):
    files_path = ""
    files_prefix = "res-line-"
    start_lambda = 1.0
    end_lambda = 3.0
    lambda_delta = 0.1

    function = ""
    fanout = 1
    threshold = 1
    job_duration = 1
    k = 10
    machine_id = 0
    bins = 10
    data_files = []

    usage = "plot_times_distribution.py"
    try:
        opts, args = getopt.getopt(
            argv, "hk:p:",
            ["files-prefix=", "start-lambda=", "end-lambda=", "lambda-delta=", "path=", "function=", "fanout=",
             "threshold=", "job-duration=", "machine-id=", "bins=", "data-files="])
    except getopt.GetoptError as e:
        print(e)
        print(usage)
        sys.exit(2)
    for opt, arg in opts:
        print(opt + " -> " + arg)
        if opt == '-h':
            print(usage)
            sys.exit()
        elif opt in ("-p", "--path"):
            files_path = arg
        elif opt in ("--files-prefix"):
            files_prefix = arg
        elif opt in ("--function"):
            function = arg
        elif opt in ("--fanout"):
            fanout = int(arg)
        elif opt in ("--threshold"):
            threshold = int(arg)
        elif opt in ("--job-duration"):
            job_duration = float(arg)
        elif opt in ("-k"):
            k = int(arg)
        elif opt in ("--start-lambda"):
            start_lambda = float(arg)
        elif opt in ("--end-lambda"):
            end_lambda = float(arg)
        elif opt in ("--lambda-delta"):
            lambda_delta = float(arg)
        elif opt in ("--machine-id"):
            machine_id = int(arg)
        elif opt in ("--bins"):
            bins = int(arg)
        elif opt in ("--data-files"):
            data_files = arg.split(":")

    if files_path == "":
        print("Some needed parameter was not given")
        print(usage)
        sys.exit()

    print("====== P2P-FOG Plot Distribution Utility ======")
    print("> files_path %s" % files_path)
    print("> files_prefix %s" % files_prefix)
    print("> start_lambda %.2f" % start_lambda)
    print("> end_lambda %.2f" % end_lambda)
    print("> lambda_delta %.2f" % lambda_delta)
    print("> function %s" % function)
    print("> fanout %d" % fanout)
    print("> threshold %d" % threshold)
    print("> job_duration %.6f" % job_duration)
    print("> k %d" % k)
    print("> machine_id %d" % machine_id)
    print("> bins %d" % bins)
    print("> data_files %s" % data_files)
    print("")

    mi = 1.0 / job_duration
    start_plot(function, files_path, files_prefix, start_lambda, end_lambda,
               lambda_delta, fanout, threshold, k, mi, machine_id, bins, data_files)


if __name__ == "__main__":
    main(sys.argv[1:])
