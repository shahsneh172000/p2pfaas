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

import math
import os
from datetime import datetime

import matplotlib.pyplot as plt

PLOT_DIRECTORY = "plot"

markers = [r"$\triangle$", r"$\square$", r"$\diamondsuit$", r"$\otimes$", r"$\star$"]


class PlotUtils:
    """Plot utilities"""

    @staticmethod
    def use_tex():
        plt.rcParams.update({
            'font.family': 'serif',
            'text.usetex': True,
            'text.latex.preamble': r"\DeclareUnicodeCharacter{03BB}{$\lambda$}"
                                   + r"\DeclareUnicodeCharacter{03BC}{$\mu$}"
                                   # + r"\usepackage[utf8]{inputenc}"
                                   + r"\usepackage{amssymb}"
                                   # + r"\usepackage[libertine]{newtxmath}"
                                   # + r"\usepackage[libertine]{newtxmath}\usepackage[T1]{fontenc}"
                                   + r"\usepackage{mathptmx}"
                                   + r"\usepackage[T1]{fontenc}"
        })
        return True


class Plot:
    @staticmethod
    def plot(x_arr, y_arr, x_label, y_label, filename, title=None, full_path=None):
        plt.clf()

        fig, ax = plt.subplots()
        line_experimental, = ax.plot(x_arr, y_arr, marker="x", markersize=3.0, markeredgewidth=1, linewidth=0.7)

        if title is not None:
            ax.set_title(title)

        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.grid(color='#cacaca', linestyle='--', linewidth=0.5)
        fig.tight_layout()

        os.makedirs(PLOT_DIRECTORY, exist_ok=True)

        path = "{}/{}.pdf".format(PLOT_DIRECTORY, filename)
        if full_path is not None:
            path = full_path

        plt.savefig(path)
        plt.close(fig)

    @staticmethod
    def plot_errorbar(x_arr, y_arr, y_err_low, y_err_high, x_label, y_label, filename="", title=None,
                      full_path=None, figwidth=6.4, figheight=4.8, x_arr_line=None, y_arr_line=None):
        plt.clf()
        fig, ax = plt.subplots()

        ax.errorbar(x_arr, y_arr,
                    yerr=[y_err_low, y_err_high],
                    marker="x", markersize=3.0, markeredgewidth=1,
                    linewidth=0.7, elinewidth=1, capsize=3)
        ax.grid(color='#cacaca', linestyle='--', linewidth=0.5)

        if x_arr_line is not None:
            ax.plot(x_arr_line, y_arr_line)

        if title is not None:
            ax.set_title(title)

        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.grid(color='#cacaca', linestyle='--', linewidth=0.5)
        fig.tight_layout()

        os.makedirs(PLOT_DIRECTORY, exist_ok=True)

        path = "{}/{}.pdf".format(PLOT_DIRECTORY, filename)
        if full_path is not None:
            path = full_path

        fig.tight_layout(h_pad=0)
        fig.set_figwidth(figwidth)  # 6.4
        fig.set_figheight(figheight)  # 4.8

        plt.savefig(path)
        plt.close(fig)

    @staticmethod
    def multi_plot(x_arr, y_arr, x_label, y_label, filename="", legend=None, title=None, log=False, full_path=None,
                   use_marker=True):
        if len(x_arr) != len(y_arr):
            print("Error, size mismatch")
            return

        plt.clf()
        fig, ax = plt.subplots()
        ax.grid(color='#cacaca', linestyle='--', linewidth=0.5)

        legend_arr = []

        for i in range(len(y_arr)):
            if use_marker:
                line, = ax.plot(x_arr[i], y_arr[i], markerfacecolor='None', linewidth=0.6,
                                marker=markers[i % len(markers)],
                                markersize=5, markeredgewidth=0.6)
            else:
                line, = ax.plot(x_arr[i], y_arr[i], markerfacecolor='None', linewidth=0.8)

            if log:
                ax.set_yscale('log')
            if legend is not None:
                legend_arr.append(line)

        if legend is not None and len(legend) == len(legend_arr):
            plt.legend(legend_arr, legend, fontsize="small")

        if title is not None:
            ax.set_title(title)

        path = "{}/{}.pdf".format(PLOT_DIRECTORY, filename)
        if full_path is not None:
            path = full_path

        # ax.set_title(title)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        fig.tight_layout()
        os.makedirs(PLOT_DIRECTORY, exist_ok=True)

        plt.savefig(path)
        plt.close(fig)


class DBUtils:

    @staticmethod
    def execute_query_for_integer(cur, query) -> int:
        res = cur.execute(query)
        dropped = 0
        has_res = False

        for line in res:
            dropped = math.ceil(line[0])

        if has_res:
            raise Exception("No output!")

        return dropped

    @staticmethod
    def execute_query_for_float(cur, query) -> float:
        res = cur.execute(query)
        dropped = 0
        has_res = False

        for line in res:
            dropped = float(line[0])

        if has_res:
            raise Exception("No output!")

        return dropped


class Utils:

    @staticmethod
    def current_time_string():
        return datetime.now().strftime("%Y%m%d-%H%M%S")
