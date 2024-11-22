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

package utils

import (
	"discovery/log"
	"net/http"
)

const UserAgentMachine = "Machine"

type Header struct {
	Field   string
	Payload string
}

type ErrorHttpCannotCreateRequest struct{}

func (e ErrorHttpCannotCreateRequest) Error() string {
	return "cannot create http request."
}

func HttpMachineGet(client *http.Client, host string, headers []Header) (*http.Response, error) {
	req, err := http.NewRequest("GET", host, nil)
	if req == nil {
		return nil, ErrorHttpCannotCreateRequest{}
	}
	req.Header.Add("User-Agent", UserAgentMachine)
	for _, header := range headers {
		req.Header.Add(header.Field, header.Payload)
	}

	res, err := client.Do(req)
	if err != nil {
		log.Log.Errorf("Error while making request to %s", host)
	}

	return res, err
}
