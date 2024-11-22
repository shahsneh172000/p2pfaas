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
	"io"
	"net/http"
	"scheduler/log"
	"time"
)

func HttpDevGet(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(200)
}

func HttpDevPost(w http.ResponseWriter, r *http.Request) {
	bytes, err := io.ReadAll(r.Body)
	if err != nil {
		log.Log.Errorf("Could not read body of request: %s", err)
	}

	timeStart := float64(time.Now().UnixMicro())
	_, err = w.Write(bytes)
	if err != nil {
		log.Log.Errorf("Could not write body of response: %s", err)
	}

	log.Log.Debugf("Elapsed for writing %.3fms", (float64(time.Now().UnixMicro())-timeStart)/1000.0)

	defer r.Body.Close()

	// w.WriteHeader(200)
}
