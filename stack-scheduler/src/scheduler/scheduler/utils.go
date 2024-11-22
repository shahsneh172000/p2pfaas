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

package scheduler

import (
	"encoding/base64"
	"encoding/json"
	"scheduler/config"
	"scheduler/log"
	"scheduler/memdb"
	"scheduler/queue"
	"scheduler/scheduler_service"
	"scheduler/types"
	"scheduler/utils"
)

/*
 * Core
 */

func executeJobExternally(serviceRequest *types.ServiceRequest, remoteNodeIP string, timingsStart *types.TimingsStart, scheduler string) (*JobResult, error) {
	log.Log.Debugf("[R#%d,T%s] %s scheduled to be run at %s", serviceRequest.Id, serviceRequest.IdTracing, serviceRequest.ServiceName, remoteNodeIP)

	if timingsStart != nil {
		timingsStart.ScheduledAt = utils.GetTimeNow()
	}

	// prepare everything to send the job externally
	peerRequest, err := prepareForwardToPeerRequest(serviceRequest)
	if err != nil {
		return nil, err
	}

	// metrics
	// metrics.PostJobIsForwarded(serviceRequest.ServiceName)

	res, err := scheduler_service.ExecuteFunction(remoteNodeIP, peerRequest)

	/* This is blocking */

	return prepareJobResultFromExternalExecution(serviceRequest, res, err, timingsStart, scheduler, remoteNodeIP)
}

func executeJobLocally(req *types.ServiceRequest, timingsStart *types.TimingsStart, scheduler string) (*JobResult, error) {
	log.Log.Debugf("[R#%d,T%s] %s scheduled to be run locally: external=%t", req.Id, req.IdTracing, req.ServiceName, req.External)

	if timingsStart != nil {
		timingsStart.ScheduledAt = utils.GetTimeNow()
	}

	freeSlots := memdb.GetFreeRunningSlots()
	if !config.GetQueueEnabled() && freeSlots <= 0 {
		log.Log.Debugf("[R#%d,T%s] %s cannot be scheduled to be run locally: freeSlots=%d", req.Id, req.IdTracing, req.ServiceName, freeSlots)
		return &JobResult{
			Response:          nil,
			Timings:           &types.Timings{},
			TimingsStart:      timingsStart,
			ExternalExecution: false,
			Scheduler:         scheduler,
		}, JobCannotBeScheduled{}
	}

	// If we execute the job locally and request is external, payload is base64encoded and we decode it
	if req.External {
		decodedPayload, _ := base64.StdEncoding.DecodeString(string(req.Payload))
		req.Payload = decodedPayload
	}

	job, err := queue.EnqueueJob(req)

	/* This is blocking */

	if err != nil {
		log.Log.Debugf("[R#%d,T%s] Cannot add job to queue, job is discarded", req.Id, req.IdTracing)
		return &JobResult{
			Response:          nil,
			Timings:           &types.Timings{},
			TimingsStart:      timingsStart,
			ExternalExecution: false,
			Scheduler:         scheduler,
		}, JobCannotBeScheduled{}
	}

	// Fill the execution time since it is derived from the internal execution
	timings := types.Timings{ExecutionTime: &job.Timings.ExecutionTime}

	return prepareJobResultFromInternalExecution(job, req, timingsStart, &timings, scheduler), nil
}

// prepareJobResultFromInternalExecution prepare the result when the job is executed internally
func prepareJobResultFromInternalExecution(job *queue.QueuedJob, req *types.ServiceRequest, timingsStart *types.TimingsStart, timings *types.Timings, scheduler string) *JobResult {
	var response *types.APIResponse

	if job.Response != nil {
		log.Log.Debugf("[R#%d,T%s] status_code=%d", req.Id, req.IdTracing, job.Response.StatusCode)

		response = &types.APIResponse{
			Headers:    job.Response.Headers,
			StatusCode: job.Response.StatusCode,
			Body:       job.Response.Body,
		}
	}

	result := JobResult{
		Response:          response,
		Timings:           timings,
		TimingsStart:      timingsStart,
		ExternalExecution: false,
		ErrorExecution:    job.ErrorExecution,
		Scheduler:         scheduler,
	}

	return &result
}

func prepareJobResultFromExternalExecution(req *types.ServiceRequest, res *scheduler_service.APIResponse, reqErr error, timingsStart *types.TimingsStart, scheduler string, remoteNodeIP string) (*JobResult, error) {
	var response types.APIResponse
	var result JobResult

	result.TimingsStart = timingsStart
	result.ExternalExecution = true
	result.Timings = &types.Timings{}
	result.Scheduler = scheduler

	// request to neighbor failed
	if reqErr != nil {
		log.Log.Errorf("[R#%d,T%s] Request to neighbor failed", req.Id, req.IdTracing)

		result.ErrorExecution = true
		return &result, JobCannotBeForwarded{
			neighborHost: remoteNodeIP,
			reason:       reqErr.Error(),
		}
	}

	// Response should be never nil but we check here in case
	if res != nil {
		log.Log.Debugf("[R#%d,T%s] Response from external execution is %d", req.Id, req.IdTracing, res.StatusCode)
		response = types.APIResponse{
			Headers:    res.Headers,
			StatusCode: res.StatusCode,
			Body:       res.Body,
		}

		var peerJobResponse types.PeerJobResponse
		err := json.Unmarshal(res.Body, &peerJobResponse)
		if err != nil {
			log.Log.Debugf("[R#%d,T%s] Cannot decode the job response", req.Id, req.IdTracing)
		}

		// Change the body of the response leaving only the output of the function, this because when executing functions
		// between peer nodes we encapsulate the output body in a PeerJobResponse struct
		response.Body = []byte(peerJobResponse.Body)

		// Prepare the result
		result.Response = &response
		result.ExternalExecutionInfo = &ExternalExecutionInfo{
			PeersList: peerJobResponse.PeersList,
		}
	} else {
		log.Log.Errorf("[R#%d,T%s] Response from peer is nil", req.Id, req.IdTracing)

		result.ErrorExecution = true
		return &result, PeerResponseNil{
			neighborHost: remoteNodeIP,
		}
	}

	return &result, nil
}

/*
 * Utils
 */

// prepareForwardToPeerRequest prepare the request to execute the job to another peer
func prepareForwardToPeerRequest(serviceRequest *types.ServiceRequest) (*types.PeerJobRequest, error) {
	peerRequest := types.PeerJobRequest{
		ServiceIdRequest: serviceRequest.Id,
		ServiceIdTracing: serviceRequest.IdTracing,
		FunctionName:     serviceRequest.ServiceName,
		ContentType:      serviceRequest.PayloadContentType,
	}

	// If request is external the payload is already in base64
	if !serviceRequest.External {
		// encode payload in base64
		peerRequest.Payload = base64.StdEncoding.EncodeToString(serviceRequest.Payload)
		peerRequest.Hops += 1
	} else {
		peerRequest.Payload = string(serviceRequest.Payload)
		peerRequest.Hops = 1
	}
	return &peerRequest, nil
}
