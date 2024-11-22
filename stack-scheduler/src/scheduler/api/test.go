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
	"net/http"
	"scheduler/log"
	"strconv"
	"time"
)

func TestDevParallelRequests(w http.ResponseWriter, r *http.Request) {
	timeForSleepSec := int64(5)

	sleepReq := r.URL.Query().Get("seconds")
	if sleepReq != "" {
		timeforSleepSecParsed, err := strconv.ParseInt(sleepReq, 10, 64)
		if err == nil {
			timeForSleepSec = timeforSleepSecParsed
		}
	}

	log.Log.Debugf("Sleeping for %d seconds...", timeForSleepSec)

	time.Sleep(time.Duration(timeForSleepSec) * time.Second)

	w.WriteHeader(200)
}
