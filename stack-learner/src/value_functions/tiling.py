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
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.

from math import floor
from typing import List

import numpy as np

from log import Log


class Tiling:
    _MODULE_NAME = "value_functions.Tiling"

    def __init__(self, num_tilings=8, max_size=1024, alpha=.01):
        self._max_size = max_size
        self._num_of_tilings = num_tilings
        self._alpha = alpha

        self._hash_table = IHT(self._max_size)
        self._weights = np.zeros(self._max_size)
        self._scale_state = self._num_of_tilings / 4

        Log.minfo(Tiling._MODULE_NAME, f"Init Tiling success: num_tilings={num_tilings}, max_size={max_size}, alpha={alpha}")

    def q_sa(self, state: List[float], action: float) -> float:
        active_tiles = self._get_active_tiles(state + [action])
        return float(np.sum(self._weights[active_tiles]))

    def max_a_q_sa(self, state: List[float]):
        return 0, 0

    def train(self, state: List[float], action: float, delta: float):
        # apply differential sarsa
        active_tiles = self._get_active_tiles(state + [action])

        for active_tile in active_tiles:
            self._weights[active_tile] += delta

        return delta

    def get_weights(self):
        return {
            "weights": self._weights
        }

    #
    # Internals
    #

    def _get_active_tiles(self, state):
        action = state[-1]
        active_tiles = tiles(self._hash_table, self._num_of_tilings,
                             [s * self._scale_state for s in state],
                             [action])
        return active_tiles


class IHT:
    """Structure to handle collisions"""

    def __init__(self, size_val):
        self.size = size_val
        self.overfull_count = 0
        self.dictionary = {}

    def count(self):
        return len(self.dictionary)

    def full(self):
        return len(self.dictionary) >= self.size

    def get_index(self, obj, read_only=False):
        d = self.dictionary
        if obj in d:
            return d[obj]
        elif read_only:
            return None
        size = self.size
        count = self.count()
        if count >= size:
            if self.overfull_count == 0:
                print('IHT full, starting to allow collisions')
            self.overfull_count += 1
            return hash(obj) % self.size
        else:
            d[obj] = count
            return count


def hash_coords(coordinates, m, read_only=False):
    if isinstance(m, IHT):
        return m.get_index(tuple(coordinates), read_only)
    if isinstance(m, int):
        return hash(tuple(coordinates)) % m
    if m is None:
        return coordinates


def tiles(iht_or_size, num_tilings, floats, ints=None, read_only=False):
    """returns num-tilings tile indices corresponding to the floats and ints"""
    if ints is None:
        ints = []
    qfloats = [floor(f * num_tilings) for f in floats]
    tiles = []
    for tiling in range(num_tilings):
        tilingX2 = tiling * 2
        coords = [tiling]
        b = tiling
        for q in qfloats:
            coords.append((q + b) // num_tilings)
            b += tilingX2
        coords.extend(ints)
        tiles.append(hash_coords(coords, iht_or_size, read_only))
    return tiles
