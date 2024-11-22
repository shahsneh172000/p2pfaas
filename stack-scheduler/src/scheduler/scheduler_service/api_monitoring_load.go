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
	"scheduler/log"
	"scheduler/utils"
)

func monitoringLoadGetApiCall(host string) (*APIResponse, error) {
	res, err := utils.HttpMachineGet(GetMonitoringLoadUrl(host))
	if err != nil {
		log.Log.Debugf("Cannot create GET request to %s", err.Error(), GetMonitoringLoadUrl(host))
		return nil, err
	}

	// body, _ := ioutil.ReadAll(res.Body)
	_ = res.Body.Close()

	response := APIResponse{
		Headers:    res.Header,
		Body:       []byte(""),
		StatusCode: res.StatusCode,
	}

	return &response, err
}
