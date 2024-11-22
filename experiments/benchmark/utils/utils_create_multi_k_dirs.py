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

import getopt
import os
import sys


def main(argv):
    out_dir = ""
    machines_n = 10
    fanout = 1
    threshold_from = 0
    threshold_to = 10
    algorithm_name = "LL"

    usage = "utils_create_multi_k_dirs.py"
    try:
        opts, args = getopt.getopt(
            argv, "h",
            ["out-dir=", "machines-n=", "fanout=", "threshold-from=", "threshold-to=", "algorithm-name="])
    except getopt.GetoptError as e:
        print("error: %s" % e)
        print(usage)
        sys.exit(2)
    for opt, arg in opts:
        # print(opt + " -> " + arg)
        if opt == '-h':
            print(usage)
            sys.exit()
        elif opt in "--out-dir":
            out_dir = arg
        elif opt in "--machines-n":
            machines_n = int(arg)
        elif opt in "--fanout":
            fanout = int(arg)
        elif opt in "--threshold-from":
            threshold_from = int(arg)
        elif opt in "--threshold-to":
            threshold_to = int(arg)
        elif opt in "--algorithm-name":
            algorithm_name = arg

    print("====== P2P-FAAS Create dirs ======")
    print("> out_dir %s" % out_dir)
    print("> machines_n %d" % machines_n)
    print("> fanout %d" % fanout)
    print("> threshold_from %s" % threshold_from)
    print("> threshold_to %d" % threshold_to)
    print("> algorithm_name %s" % algorithm_name)
    print("")

    if out_dir == "":
        print("Out dir cannot be empty")
        print(usage)
        sys.exit()

    for i in range(threshold_from, threshold_to + 1):
        to_make_dir = "{}/{}({},{})-{}machines".format(out_dir, algorithm_name, fanout, i, machines_n)
        print("> Creating dir %s" % to_make_dir)
        os.makedirs(to_make_dir, exist_ok=True)


if __name__ == "__main__":
    main(sys.argv[1:])
