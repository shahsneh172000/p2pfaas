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

package api

import (
	"encoding/json"
	"io"
	"net/http"
	"scheduler/config"
	"scheduler/log"
)

type HelloResponse struct {
	Name          string `json:"name"`
	Version       string `json:"version"`
	VersionCommit string `json:"version_commit"`
}

func Hello(w http.ResponseWriter, r *http.Request) {
	log.Log.Debugf("called by %s", r.RemoteAddr)

	helloRes := HelloResponse{
		Name:          config.AppName,
		Version:       config.AppVersion,
		VersionCommit: config.AppVersionCommit,
	}
	resBytes, _ := json.Marshal(helloRes)

	_, _ = io.WriteString(w, string(resBytes))
}
