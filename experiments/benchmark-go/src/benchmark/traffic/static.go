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

import "benchmark/log"

const modelStaticName = "ModelStatic"

type ModelStatic struct {
	loadArray []float64
}

func (m ModelStatic) Init() error {
	log.Log.Infof("Model init with loadArray=%v", m.loadArray)
	return nil
}

func (m ModelStatic) GetLoadAt(nodeIndex int, time float64) float64 {
	return m.loadArray[nodeIndex]
}

func (m ModelStatic) GetName() string {
	return modelStaticName
}

/*
 * Creation
 */

func CreateModelStatic(loadArray []float64) *ModelStatic {
	return &ModelStatic{loadArray: loadArray}
}
