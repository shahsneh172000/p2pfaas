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

package api_peer

import (
	"encoding/base64"
	"encoding/json"
	"github.com/gorilla/mux"
	"io/ioutil"
	"net/http"
	"reflect"
	"scheduler/api"
	"scheduler/config"
	"scheduler/errors"
	"scheduler/log"
	"scheduler/memdb"
	"scheduler/scheduler"
	"scheduler/service_discovery"
	"scheduler/types"
	"scheduler/utils"
)

// FunctionExecute Execute a function. This function must called only by another node, and not a client.
func FunctionExecute(w http.ResponseWriter, r *http.Request) {
	var requestId uint64 = 0
	tracingId := api.HeadersGetRequestTracingId(r)

	if !headersCheckUserAgentMachine(r) {
		errors.ReplyWithError(&w, errors.GenericError, nil)
		log.Log.Errorf("[R#%d,T%s] called from not a machine", requestId, tracingId)
		return
	}

	// assign id to requests if development
	if log.GetEnv() != config.RunningEnvironmentProduction {
		requestId = memdb.GetNextRequestNumberFromPeers()
	}

	log.Log.Debugf("[R#%d,T%s] Request to execute function from peer %s", requestId, tracingId, r.RemoteAddr)

	vars := mux.Vars(r)
	function := vars["function"]
	if function == "" {
		errors.ReplyWithError(&w, errors.GenericError, nil)
		log.Log.Debugf("[R#%d,T%s] service is not specified", requestId, tracingId)
		return
	}

	bytes, err := ioutil.ReadAll(r.Body)
	if err != nil {
		log.Log.Errorf("[R#%d,T%s] Cannot parse input: %s", requestId, tracingId, err)
		errors.ReplyWithError(&w, errors.InputNotValid, nil)
		return
	}

	var peerRequest types.PeerJobRequest
	err = json.Unmarshal(bytes, &peerRequest)
	if err != nil {
		log.Log.Errorf("[R#%d,T%s] Cannot parse json input: %s", requestId, tracingId, err)
		errors.ReplyWithError(&w, errors.InputNotValid, nil)
		return
	}

	peerRequest.ServiceIdRequest = requestId
	peerRequest.ServiceIdTracing = tracingId

	serviceRequest := types.ServiceRequest{
		Id:                 requestId,
		IdTracing:          tracingId,
		External:           true,
		ExternalJobRequest: &peerRequest,
		ServiceName:        function,
		Payload:            []byte(peerRequest.Payload), // the payload is a string because request it's a peer request
		PayloadContentType: peerRequest.ContentType,
		Headers:            utils.HttpParseXHeaders(r.Header),
	}

	log.Log.Debugf("[R#%d,T%s] type=%s, len(payload)=%d", requestId, tracingId, serviceRequest.PayloadContentType, len(serviceRequest.Payload))
	log.Log.Debugf("[R#%d,T%s] len(peers)=%d, service=%s", requestId, tracingId, len(peerRequest.PeersList), serviceRequest.ServiceName)

	// schedule the job
	jobResult, err := scheduler.Schedule(&serviceRequest)

	// prepare response
	peerResponse := preparePeerResponse(&peerRequest, &serviceRequest, jobResult, err)

	responseBodyBytes, err := json.Marshal(peerResponse)
	if err != nil {
		log.Log.Errorf("[R#%d,T%s] Cannot marshal peerResponse: %s", requestId, tracingId, err)
		errors.ReplyWithError(&w, errors.MarshalError, nil)
		return
	}

	utils.HttpSendJSONResponse(&w, peerResponse.StatusCode, string(responseBodyBytes), nil)
}

// preparePeerResponse Prepares the response to another peer that invoked the function. Remember: jobResult MUST NOT be
// nil even if there is a scheduleErr!
func preparePeerResponse(peerRequest *types.PeerJobRequest, serviceRequest *types.ServiceRequest, jobResult *scheduler.JobResult, scheduleErr error) *types.PeerJobResponse {
	log.Log.Debugf("[R#%d,T%s] Preparing peer response of job", serviceRequest.Id, peerRequest.ServiceIdTracing)

	var res = types.PeerJobResponse{}

	utils.ComputeTimings(jobResult.TimingsStart, jobResult.Timings)

	// when job ends add us in the peers list
	if jobResult.ExternalExecution {
		log.Log.Debugf("[R#%d,T%s] Job has been executed externally", serviceRequest.Id, peerRequest.ServiceIdTracing)
		// job has been executed externally even in from this node so external execution info is not nil
		jobResult.ExternalExecutionInfo.PeersList = append(jobResult.ExternalExecutionInfo.PeersList, service_discovery.GetPeerDescriptor(jobResult.Timings))
	} else {
		log.Log.Debugf("[R#%d,T%s] Job has been executed internally", serviceRequest.Id, peerRequest.ServiceIdTracing)
		jobResult.ExternalExecutionInfo = &scheduler.ExternalExecutionInfo{
			PeersList: []types.PeersListMember{service_discovery.GetPeerDescriptor(jobResult.Timings)},
		}
	}

	res.PeersList = jobResult.ExternalExecutionInfo.PeersList
	res.Body = ""

	// add response body
	if jobResult.Response != nil && jobResult.Response.Body != nil {
		res.Body = string(jobResult.Response.Body)
		res.StatusCode = 200
	}

	// parse scheduler error
	if scheduleErr != nil {
		log.Log.Debugf("[R#%d,T%s] Job has scheduler error [%s]: %s ", peerRequest.ServiceIdRequest, peerRequest.ServiceIdTracing, reflect.TypeOf(scheduleErr), scheduleErr)

		// compute the error json
		var errorStatusCode = -1
		var errorJsonString = ""
		var err error

		if _, ok := scheduleErr.(scheduler.JobCannotBeScheduled); ok {
			errorStatusCode, errorJsonString, err = errors.GetErrorJsonMessage(errors.JobCannotBeScheduledError, scheduleErr.Error())
			log.Log.Debugf("[R#%d,T%s] %s", peerRequest.ServiceIdRequest, peerRequest.ServiceIdTracing, scheduleErr.Error())
		} else if _, ok = scheduleErr.(scheduler.JobDeliberatelyRejected); ok {
			errorStatusCode, errorJsonString, err = errors.GetErrorJsonMessage(errors.JobDeliberatelyRejected, scheduleErr.Error())
			log.Log.Debugf("[R#%d,T%s] %s", peerRequest.ServiceIdRequest, peerRequest.ServiceIdTracing, scheduleErr.Error())
		} else if _, ok = scheduleErr.(scheduler.CannotRetrieveAction); ok {
			errorStatusCode, errorJsonString, err = errors.GetErrorJsonMessage(errors.CannotRetrieveAction, scheduleErr.Error())
			log.Log.Errorf("[R#%d,T%s] %s", peerRequest.ServiceIdRequest, peerRequest.ServiceIdTracing, scheduleErr.Error())
		} else if _, ok = scheduleErr.(scheduler.JobCannotBeForwarded); ok {
			errorStatusCode, errorJsonString, err = errors.GetErrorJsonMessage(errors.JobCouldNotBeForwarded, scheduleErr.Error())
			log.Log.Errorf("[R#%d,T%s] %s", peerRequest.ServiceIdRequest, peerRequest.ServiceIdTracing, scheduleErr.Error())
		} else if _, ok = scheduleErr.(scheduler.PeerResponseNil); ok {
			errorStatusCode, errorJsonString, err = errors.GetErrorJsonMessage(errors.PeerResponseNil, scheduleErr.Error())
			log.Log.Errorf("[R#%d,T%s] %s", peerRequest.ServiceIdRequest, peerRequest.ServiceIdTracing, scheduleErr.Error())
		} else {
			errorStatusCode, errorJsonString, err = errors.GetErrorJsonMessage(errors.GenericError, scheduleErr.Error())
			log.Log.Errorf("[R#%d,T%s] %s", peerRequest.ServiceIdRequest, peerRequest.ServiceIdTracing, scheduleErr.Error())
		}

		log.Log.Debugf("[R#%d,T%s] Job with error prepared status=%d json=%s", peerRequest.ServiceIdRequest, peerRequest.ServiceIdTracing, errorStatusCode, errorJsonString)

		if err != nil {
			log.Log.Errorf("Cannot prepare error json to return")
		}

		res.StatusCode = errorStatusCode
		res.Body = errorJsonString
	}

	// check if result has a response body
	if res.Body != "" {
		// If we have a peer request and we finally executed it here we need to encode the payload in base64
		// We are the last node of the chain PC --> O --> O --> O <-this
		if !jobResult.ExternalExecution {
			// We need to base64 encode the output
			res.Body = base64.StdEncoding.EncodeToString([]byte(res.Body))
		} // else {
		//	res.Body = string(jobResult.Response.Body) // job result from other nodes is always a base64 string
		//}
	}

	return &res
}
