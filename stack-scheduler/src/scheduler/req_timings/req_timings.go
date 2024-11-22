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

// Package req_timings implements a hashtable for storing timings in a effective way.
package req_timings

import (
	"fmt"
	"scheduler/hashtable"
	"scheduler/log"
)

var ht hashtable.ValueHashtable

func init() {
	ht = hashtable.ValueHashtable{}
}

func AddTiming(remoteAddress string, timing int64) error {
	// get current values
	values := ht.Get(remoteAddress)
	if values == nil {
		ht.Put(remoteAddress, []int64{timing})
		return nil
	}

	if valuesArr, ok := values.([]int64); ok {
		valuesArr = append(valuesArr, timing)
		if len(valuesArr) > 2 {
			valuesArr = valuesArr[1:]
		}
		ht.Put(remoteAddress, valuesArr)
	} else {
		log.Log.Errorf("Existing value is not a float arr")
	}

	return nil
}

func GetTimings(remoteAddress string) ([]int64, error) {
	values := ht.Get(remoteAddress)

	if valuesArr, ok := values.([]int64); ok {
		return valuesArr, nil
	}

	return []int64{}, fmt.Errorf("no timing for address %s", remoteAddress)
}

func Clear() {
	ht = hashtable.ValueHashtable{}
}
