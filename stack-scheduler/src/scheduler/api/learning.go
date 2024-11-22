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
	"scheduler/service_learning"
	"time"
)

var learningDevTestEid = 0

func LearningDevTestAct(w http.ResponseWriter, r *http.Request) {
	entry := service_learning.EntryAct{State: []float64{1.0, 2.3, 1.8}}
	action, err := service_learning.Act(&entry)

	if err != nil {
		log.Log.Errorf("Cannot take decision: %s", err)
	} else {
		log.Log.Debugf("Taken decision: %f", action)
	}

	w.WriteHeader(200)
}

func LearningDevTestActWs(w http.ResponseWriter, r *http.Request) {
	timeStart := time.Now()

	entry := service_learning.EntryAct{State: []float64{1.0, 2.3, 1.8}}
	action, err := service_learning.SocketAct(&entry)

	timeEnd := time.Now()

	if err != nil {
		log.Log.Errorf("Cannot take decision: %s", err)
	} else {
		log.Log.Debugf("Taken decision: %f", action)
	}

	log.Log.Debugf("Elapsed time: %fms", (float64(timeEnd.UnixNano())-float64(timeStart.UnixNano()))/1000000)

	w.WriteHeader(200)
}

func LearningDevTestTrain(w http.ResponseWriter, r *http.Request) {
	entry := service_learning.EntryLearning{
		Eid:    learningDevTestEid,
		State:  []float64{1.2, 1.0, 1.6},
		Action: 2,
		Reward: 1.3,
	}
	err := service_learning.Train(&entry)

	learningDevTestEid += 1

	if err != nil {
		log.Log.Errorf("Cannot take decision: %s", err)
	} else {
		log.Log.Debugf("Ok")
	}

	w.WriteHeader(200)
}
