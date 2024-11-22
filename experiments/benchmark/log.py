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

from __future__ import annotations

import io
import time
from threading import Lock

"""
Implement a colored logging
"""


class Colors:
    """Colors list"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class status_str:
    CHECK_STR = " " + Colors.WARNING + "CHCK" + Colors.ENDC + " "
    OK_STR = "  " + Colors.OKGREEN + "OK" + Colors.ENDC + "  "
    DEAD_STR = " " + Colors.FAIL + "DEAD" + Colors.ENDC + " "
    MISM_STR = " " + Colors.WARNING + "MISM" + Colors.ENDC + " "
    WARN_STR = " " + Colors.WARNING + "WARN" + Colors.ENDC + " "


COLOR = True


class Log(object):
    _print_lock = Lock()

    @staticmethod
    def _get_time():
        return time.strftime("%b %d %Y %H:%M:%S", time.gmtime(time.time()))

    @staticmethod
    def err(*args, **kwargs):
        new_args, new_kwargs = Log.__add_to_line_type_time("ERR", *args, **kwargs)
        if COLOR:
            new_args, new_kwargs = Log.__add_to_line_color(Colors.FAIL, *new_args, **new_kwargs)
            Log._print(*new_args, **new_kwargs)
        else:
            Log._print(*new_args, **new_kwargs)

    @staticmethod
    def fatal(*args, **kwargs):
        new_args, new_kwargs = Log.__add_to_line_type_time("FAT", *args, **kwargs)
        if COLOR:
            new_args, new_kwargs = Log.__add_to_line_color(Colors.FAIL, *new_args, **new_kwargs)
            Log._print(*new_args, **new_kwargs)
        else:
            Log._print(*new_args, **new_kwargs)

        raise RuntimeError(Log._print_to_string(*args, **kwargs))

    @staticmethod
    def warn(*args, **kwargs):
        new_args, new_kwargs = Log.__add_to_line_type_time("WRN", *args, **kwargs)
        if COLOR:
            new_args, new_kwargs = Log.__add_to_line_color(Colors.WARNING, *new_args, **new_kwargs)
            Log._print(*new_args, **new_kwargs)
        else:
            Log._print(*new_args, **new_kwargs)

    @staticmethod
    def info(*args, **kwargs):
        new_args, new_kwargs = Log.__add_to_line_type_time("INF", *args, **kwargs)
        if COLOR:
            new_args, new_kwargs = Log.__add_to_line_color(Colors.OKBLUE, *new_args, **new_kwargs)
            Log._print(*new_args, **new_kwargs)
        else:
            Log._print(*new_args, **new_kwargs)

    @staticmethod
    def debug(*args, **kwargs):
        # if not ConfigurationStatic.instance().is_development():
        #     return

        new_args, new_kwargs = Log.__add_to_line_type_time("DEB", *args, **kwargs)
        Log._print(*new_args, **new_kwargs)

    #
    # Module log
    #

    @staticmethod
    def merr(module, *args, **kwargs):
        new_args, new_kwargs = Log.__add_to_line_module(module, *args, **kwargs)
        Log.err(*new_args, **new_kwargs)

    @staticmethod
    def mwarn(module, *args, **kwargs):
        new_args, new_kwargs = Log.__add_to_line_module(module, *args, **kwargs)
        Log.warn(*new_args, **new_kwargs)

    @staticmethod
    def minfo(module, *args, **kwargs):
        new_args, new_kwargs = Log.__add_to_line_module(module, *args, **kwargs)
        Log.info(*new_args, **new_kwargs)

    @staticmethod
    def mdebug(module, *args, **kwargs):
        new_args, new_kwargs = Log.__add_to_line_module(module, *args, **kwargs)
        Log.debug(*new_args, **new_kwargs)

    @staticmethod
    def mfatal(module, *args, **kwargs):
        new_args, new_kwargs = Log.__add_to_line_module(module, *args, **kwargs)
        Log.fatal(*new_args, **new_kwargs)

    #
    # Utils
    #

    @staticmethod
    def __add_to_line_module(module, *args, **kwargs):
        new_arg0 = "[" + module + "] " + args[0] if len(args) > 0 else ""
        new_args, kwargs = Log.__replace_args_kwargs(args, kwargs, new_arg0)
        return new_args, kwargs

    @staticmethod
    def __add_to_line_type_time(type_str, *args, **kwargs):
        new_arg0 = f"{Log._get_time()} {type_str} {args[0] if len(args) > 0 else ''}"
        new_args, kwargs = Log.__replace_args_kwargs(args, kwargs, new_arg0)
        return new_args, kwargs

    @staticmethod
    def __add_to_line_color(color, *args, **kwargs):
        new_arg0 = f"{color}{args[0] if len(args) > 0 else ''}{Colors.ENDC}"
        new_args, kwargs = Log.__replace_args_kwargs(args, kwargs, new_arg0)
        return new_args, kwargs

    @staticmethod
    def __replace_args_kwargs(args, kwargs, new_arg0):
        if len(args) <= 1:
            new_args = (new_arg0,)
        else:
            new_args = (new_arg0, args[1:])

        return new_args, kwargs

    @staticmethod
    def _print(*args, **kwargs):
        Log._print_lock.acquire()
        print(*args, **kwargs)
        Log._print_lock.release()

    @staticmethod
    def _log_line(type_str, *args, **kwargs):
        return f"{Log._get_time()} {type_str} {args[0]}"

    @staticmethod
    def _print_to_string(*args, **kwargs):
        output = io.StringIO()
        print(*args, file=output, **kwargs)
        contents = output.getvalue()
        output.close()
        return contents
