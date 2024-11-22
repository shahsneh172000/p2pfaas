/*
 * P2PFaaS - A framework for FaaS Load Balancing
 * Copyright (c) 2019. Gabriele Proietti Mattia <pm.gabriele@outlook.com>
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

package watcher

import (
	"discovery/config"
	"discovery/discovery_service"
	"discovery/utils"
	"net/http"
	"time"
)

func GetForPoll(ip string) (*http.Response, error) {
	headers := []utils.Header{
		{Field: config.GetParamIp, Payload: config.GetMachineIp()},
		{Field: config.GetParamName, Payload: config.GetMachineId()},
		{Field: config.GetParamGroupName, Payload: config.GetMachineGroupName()},
	}
	client := http.Client{Timeout: time.Duration(config.GetPollTimeout()) * time.Second}
	return utils.HttpMachineGet(&client, discovery_service.GetServerListApi(ip), headers)
}
