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

package scheduler_service

import (
	"scheduler/api/api_monitoring"
	"scheduler/log"
	"scheduler/types"
	"strconv"
)

// GetLoad allows to get the load of another machine, from a machine
func GetLoad(host string) (int, *APIResponse, error) {
	res, err := monitoringLoadGetApiCall(host)
	if err != nil {
		log.Log.Debugf("Cannot get load from scheduler service: %s", err.Error())
		return -1, res, err
	}

	currentRunningFunctions, err := strconv.Atoi(res.Headers.Get(api_monitoring.ApiMonitoringLoadHeaderKey))
	if err != nil {
		log.Log.Debugf("Cannot get load from scheduler service: %s", err.Error())
		return -1, res, err
	}

	queueLen, err := strconv.Atoi(res.Headers.Get(api_monitoring.ApiMonitoringQueueLengthHeaderKey))
	if err != nil {
		log.Log.Debugf("Cannot get load from scheduler service: %s", err.Error())
		return -1, res, err
	}

	return currentRunningFunctions + queueLen, nil, nil
}

// ExecuteFunction allows to request another machine to execute a function
func ExecuteFunction(host string, peerRequest *types.PeerJobRequest) (*APIResponse, error) {
	res, err := peerFunctionApiCall(host, peerRequest)
	if err != nil {
		log.Log.Errorf("[R#%d,T%s] Cannot execute function on peer: %s", peerRequest.ServiceIdRequest, peerRequest.ServiceIdTracing, err.Error())
		return res, err
	}

	return res, nil
}
