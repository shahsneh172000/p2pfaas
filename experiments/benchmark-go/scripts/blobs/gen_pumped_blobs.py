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

from shutil import copyfile
import os

BLOB_PATH = "."
BLOB_NAME = "family"
BLOB_EXTENSION = "jpg"


def gen(size):
    """Size in bytes"""
    original_file = f"{BLOB_PATH}/{BLOB_NAME}.{BLOB_EXTENSION}"
    original_size = os.path.getsize(original_file)
    print(original_size)

    new_file = f"{BLOB_PATH}/{BLOB_NAME}_{size}bytes.{BLOB_EXTENSION}"
    copyfile(original_file, new_file)
    print(new_file)

    bytes_to_write = size-original_size
    blob_file = open(new_file, "ab")
    for i in range(bytes_to_write):
        blob_file.write(b'0')
    blob_file.close()

gen(50000)  # 50kb
for i in range(1, 10):
    gen(i*100000)  # 100kb
