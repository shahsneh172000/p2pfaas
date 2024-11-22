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

package faas

import (
	"scheduler/config"
	"scheduler/faas_containers"
	"scheduler/faas_openfaas"
	"scheduler/types"
)

// FunctionExecute execute the FaaS function by selecting the appropriate dispatcher
func FunctionExecute(functionName string, payload []byte, contentType string) (*types.FaasApiResponse, error) {
	if config.GetOpenFaasEnabled() {
		return faas_openfaas.FunctionExecute(functionName, payload, contentType)
	} else {
		return faas_containers.FunctionExecute(functionName, payload, contentType)
	}
}
