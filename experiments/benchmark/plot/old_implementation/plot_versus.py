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
import model_mm1k

# LaTex plot init
# USE_TEX = PlotUtils.use_tex()
USE_TEX = False

DICT_LAMBDA = "lambda"
DICT_PB = "pb"
DICT_DELAY = "delay"
DICT_PE = "pe"


def parseLogFile(file_path):
    in_file = open(file_path, "r")
    d = {"lambda": [], "pb": [], "delay": [], "pe": []}

    for line in in_file:
        comps = line.split()
        d[DICT_LAMBDA].append(float(comps[0]))
        d[DICT_PB].append(float(comps[1]))
        d[DICT_DELAY].append(float(comps[2]))
        d[DICT_PE].append(float(comps[3]))

    in_file.close()
    return d


def start_plot(first_file, second_file, first_title, second_title, x_axis, y_axis, out_dir, model_name, model_k,
               model_job_len):
    file_1 = parseLogFile(first_file)
    file_2 = parseLogFile(second_file)

    def plotData(feature, dict_1, dict_2, dict_model=None):
        print("{}-{}-vs-{}".format(feature, first_title, second_title))
        plt.clf()
        line_1, = plt.plot(dict_1[DICT_LAMBDA], dict_1[feature], c="C0")
        line_2, = plt.plot(dict_2[DICT_LAMBDA], dict_2[feature], c="C2")

        if dict_model != None:
            line_model, = plt.plot(dict_1[DICT_LAMBDA], dict_model, c="C1")
            plt.legend([line_1, line_2, line_model], [first_title, second_title, model_name])
        else:
            plt.legend([line_1, line_2], [first_title, second_title])

        # plt.title("{0} - LL({1}, K-{2}) - (K={3},μ={4:.4f}) - Machine#{5}".format(function, f, t, k, mi, i))
        plt.xlabel(x_axis)
        plt.ylabel(feature)

        if dict_model != None:
            plt.savefig("{}/{}-{}-vs-{}-with-model.pdf".format(out_dir, feature, first_title, second_title))
        else:
            plt.savefig("{}/{}-{}-vs-{}.pdf".format(out_dir, feature, first_title, second_title))

    os.makedirs(out_dir, exist_ok=True)

    if model_name == "":
        plotData(DICT_DELAY, file_1, file_2)
        plotData(DICT_PB, file_1, file_2)
        plotData(DICT_PE, file_1, file_2)
    else:
        plotData(DICT_DELAY, file_1, file_2, model_mm1k.generateDelayArray(
            file_1[DICT_LAMBDA], model_k, 1.0 / model_job_len))
        plotData(DICT_PB, file_1, file_2, model_mm1k.generatePbArray(file_1[DICT_LAMBDA], model_k, 1.0 / model_job_len))
        plotData(DICT_PE, file_1, file_2)


def main(argv):
    first_file = ""
    second_file = ""
    first_title = ""
    second_title = ""
    x_axis = ""
    y_axis = ""
    out_dir = ""

    model_name = ""
    model_k = 10
    model_job_len = 1

    usage = "plot_versus.py"
    try:
        opts, args = getopt.getopt(
            argv, "h",
            ["first-file=", "second-file=", "first-title=", "second-title=", "x-axis=", "y-axis=", "out-dir=",
             "model-name=", "model-k=", "model-job-len="])
    except getopt.GetoptError:
        print(usage)
        sys.exit(2)
    for opt, arg in opts:
        # print(opt + " -> " + arg)
        if opt == '-h':
            print(usage)
            sys.exit()
        elif opt in "--first-file":
            first_file = arg
        elif opt in "--second-file":
            second_file = arg
        elif opt in "--first-title":
            first_title = arg
        elif opt in "--second-title":
            second_title = arg
        elif opt in "--x-axis":
            x_axis = arg
        elif opt in "--y-axis":
            y_axis = arg
        elif opt in "--out-dir":
            out_dir = arg
        elif opt in "--model-name":
            model_name = arg
        elif opt in "--model-k":
            model_k = int(arg)
        elif opt in "--model-job-len":
            model_job_len = float(arg)

    if first_file == "":
        print("Some needed parameter was not given")
        print(usage)
        sys.exit()

    print("====== P2P-FOG Plot Utilities ======")
    print("> first_file %s" % first_file)
    print("> second_file %s" % second_file)
    print("> first_title %s" % first_title)
    print("> second_title %s" % second_title)
    print("> x_axis %s" % x_axis)
    print("> y_axis %s" % y_axis)
    print("----")
    print("> model_name %s" % model_name)
    print("> model_k %s" % model_k)
    print("> model_job_len %s" % model_job_len)
    print("----")
    print("> out_dir %s" % out_dir)
    print("")

    start_plot(first_file, second_file, first_title, second_title, x_axis,
               y_axis, out_dir, model_name, model_k, model_job_len)


if __name__ == "__main__":
    main(sys.argv[1:])
