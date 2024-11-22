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
	"fmt"
	"github.com/gorilla/mux"
	"io/ioutil"
	"net/http"
	"scheduler/errors"
	"scheduler/log"
	"scheduler/memdb"
	"scheduler/metrics"
	"scheduler/scheduler"
	"scheduler/service_discovery"
	"scheduler/types"
	"scheduler/utils"
)

func FunctionPost(w http.ResponseWriter, r *http.Request) {
	executeFunction(w, r)
}

func FunctionGet(w http.ResponseWriter, r *http.Request) {
	executeFunction(w, r)
}

/*
 * utils
 */

func executeFunction(w http.ResponseWriter, r *http.Request) {
	var err error
	var jobResult *scheduler.JobResult
	tracingId := HeadersGetRequestTracingId(r)

	vars := mux.Vars(r)
	function := vars["function"]
	if function == "" {
		errors.ReplyWithErrorMessage(&w, errors.GenericError, fmt.Sprintf("[T%s] service is not specified", tracingId), nil)
		log.Log.Debugf("[T%s] service is not specified", tracingId)
		return
	}

	var requestId uint64 = 0
	// assign id to requests if development
	// if log.GetEnv() != config.RunningEnvironmentProduction {
	requestId = memdb.GetNextRequestNumber()
	//}

	log.Log.Debugf("[R#%d,T%s] Execute function called for %s", requestId, tracingId, function)

	payload, _ := ioutil.ReadAll(r.Body)
	req := types.ServiceRequest{
		Id:                 requestId,
		IdTracing:          tracingId,
		ServiceName:        function,
		Payload:            payload,
		PayloadContentType: r.Header.Get("Content-Type"),
		External:           false,
		Headers:            utils.HttpParseXHeaders(r.Header),
	}

	// schedule the function execution forced if development
	// if config.IsRunningEnvironmentDevelopment() {
	if headersCheckSchedulerBypass(r) {
		jobResult, err = scheduler.ScheduleBypassAlgorithm(&req)
	} else if headersCheckSchedulerForward(r) {
		jobResult, err = scheduler.ScheduleForward(&req)
	} else if headersCheckSchedulerReject(r) {
		jobResult, err = scheduler.ScheduleReject(&req)
	} else {
		jobResult, err = scheduler.Schedule(&req)
	}

	/* This is blocking */

	// check if any error
	if err != nil {
		if _, ok := err.(scheduler.JobCannotBeScheduled); ok {
			ReplyWithErrorFromJobResult(&w, errors.JobCannotBeScheduledError, jobResult, err.Error())
			log.Log.Debugf("[R#%d,T%s] %s", requestId, tracingId, err.Error())
			return
		}
		if _, ok := err.(scheduler.JobDeliberatelyRejected); ok {
			ReplyWithErrorFromJobResult(&w, errors.JobDeliberatelyRejected, jobResult, err.Error())
			log.Log.Debugf("[R#%d,T%s] %s", requestId, tracingId, err.Error())
			return
		}
		if _, ok := err.(scheduler.CannotRetrieveAction); ok {
			ReplyWithErrorFromJobResult(&w, errors.CannotRetrieveAction, jobResult, err.Error())
			log.Log.Errorf("[R#%d,T%s] %s", requestId, tracingId, err.Error())
			return
		}
		if _, ok := err.(scheduler.JobCannotBeForwarded); ok {
			ReplyWithErrorFromJobResult(&w, errors.JobCouldNotBeForwarded, jobResult, err.Error())
			log.Log.Errorf("[R#%d,T%s] %s", requestId, tracingId, err.Error())
			return
		}
		if _, ok := err.(scheduler.PeerResponseNil); ok {
			ReplyWithErrorFromJobResult(&w, errors.PeerResponseNil, jobResult, err.Error())
			log.Log.Errorf("[R#%d,T%s] %s", requestId, tracingId, err.Error())
			return
		}
		if _, ok := err.(scheduler.CannotRetrieveRecipientNode); ok {
			ReplyWithErrorFromJobResult(&w, errors.CannotRetrieveRecipientNode, jobResult, err.Error())
			log.Log.Errorf("[R#%d,T%s] %s", requestId, tracingId, err.Error())
			return
		}
		ReplyWithErrorFromJobResult(&w, errors.GenericError, jobResult, fmt.Sprintf("[R#%d,T%s] Cannot schedule the service request: %s", requestId, tracingId, err.Error()))
		log.Log.Debugf("[R#%d,T%s] Cannot schedule the service request: %s", requestId, tracingId, err.Error())
		return
	}

	// check results
	if jobResult != nil && jobResult.Response != nil {
		log.Log.Debugf("[R#%d,T%s] Execute function called for %s done: statusCode=%d", requestId, tracingId, function, jobResult.Response.StatusCode)
	} else if jobResult == nil {
		log.Log.Errorf("[R#%d,T%s] jobResult is nil", requestId, tracingId)
		ReplyWithErrorFromJobResult(&w, errors.GenericError, jobResult, fmt.Sprintf("[R#%d,T%s] jobResult is nil", requestId, tracingId))
		return
	} else if jobResult.Response == nil {
		log.Log.Errorf("[R#%d,T%s] jobResult.Response is nil", requestId, tracingId)
		ReplyWithErrorFromJobResult(&w, errors.GenericError, jobResult, fmt.Sprintf("[R#%d,T%s] jobResult.Response is nil", requestId, tracingId))
		return
	}

	// Compute timings
	utils.ComputeTimings(jobResult.TimingsStart, jobResult.Timings)

	// Add us in list if job is executed externally
	if jobResult.ExternalExecution && jobResult.ExternalExecutionInfo.PeersList != nil {
		jobResult.ExternalExecutionInfo.PeersList = append(
			jobResult.ExternalExecutionInfo.PeersList,
			service_discovery.GetPeerDescriptor(jobResult.Timings),
		)
	} else if jobResult.ExternalExecution && jobResult.ExternalExecutionInfo.PeersList == nil {
		log.Log.Fatalf("[R#%d,T%s] Job has been executed externally but its peers list is empty", requestId, tracingId)
	}

	// reply to client
	ReplyWithBodyFromJobResult(&req, &w, jobResult)

	// metrics
	defer metrics.PostJobInvocations(function, jobResult.Response.StatusCode)

	defer log.Log.Debugf("[R#%d,T%s] %s success", requestId, tracingId, function)
}
