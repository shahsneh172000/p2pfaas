/*
 * P2PFaaS - A framework for FaaS Load Balancing
 * Copyright (c) 2019 - 2022. Gabriele Proietti Mattia <pm.gabriele@outlook.com>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

package learning

import "benchmark/types"

// RewardFromDeadline assigns the reward given the deadline (expressed in seconds)
func RewardFromDeadline(result *types.BenchmarkResult, deadlines []float64) float64 {
	if result.TypeId > int64(len(deadlines))-1 {
		return -1.0
	}

	if result.ResponseStatusCode == 200 && result.TimeTotal <= deadlines[result.TypeId] {
		return 1.0
	}

	return 0.0
}
