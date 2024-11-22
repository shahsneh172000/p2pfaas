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

package traffic

import (
	"benchmark/log"
	"testing"
)

func TestTraffic(t *testing.T) {
	log.SetDebug(true)

	totalTime := 300.0
	nNodes := 12

	log.Log.Debugf("Creating model")

	model := CreateModelDynamic(
		"../../../scripts/traffic",
		"traffic_node_",
		"csv",
		int64(nNodes),
		1.0,
		16.0,
		totalTime,
		0,
		3.0,
	)

	err := model.Init()
	if err != nil {
		log.Log.Errorf("Model cannot be initialized: %s", err)
		return
	}

	for time := 0.0; time < totalTime; time++ {
		// for i := 0; i < nNodes; i++ {
		log.Log.Debugf("node %d time %f value %f", 0, time, model.GetLoadAt(0, time))
		// }
	}
}
