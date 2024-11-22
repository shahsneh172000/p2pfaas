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
	"encoding/base64"
	"encoding/json"
	"fmt"
	"net/http"
	"scheduler/config"
	"scheduler/errors"
	"scheduler/log"
	"scheduler/scheduler"
	"scheduler/types"
	"scheduler/utils"
)

/*
 * Utils
 */

func headersCheckSchedulerBypass(req *http.Request) bool {
	return req.Header.Get(utils.HttpHeaderP2PFaaSSchedulerBypass) != ""
}

func headersCheckSchedulerForward(req *http.Request) bool {
	return req.Header.Get(utils.HttpHeaderP2PFaaSSchedulerForward) != ""
}

func headersCheckSchedulerReject(req *http.Request) bool {
	return req.Header.Get(utils.HttpHeaderP2PFaaSSchedulerReject) != ""
}

func HeadersGetRequestTracingId(req *http.Request) string {
	return req.Header.Get(utils.HttpHeaderP2PFaaSSchedulerTracingId)
}

func HttpGetHeadersFromFramework() map[string]string {
	return map[string]string{
		utils.HttpHeaderP2PFaaSVersion:   config.AppVersion,
		utils.HttpHeaderP2PFaaSScheduler: scheduler.GetName(),
	}
}

func HttpGetHeadersFromJobResult(result *scheduler.JobResult) map[string]string {
	if result == nil {
		return map[string]string{}
	}

	// add base headers
	output := map[string]string{
		utils.HttpHeaderP2PFaaSScheduler: result.Scheduler,
	}

	// add headers from job result
	if result.ResponseHeaders != nil {
		output = utils.MapsMerge(output, *result.ResponseHeaders)
	}

	return output
}

func HttpGetHeadersXFromResponse(apiResponse *types.APIResponse) map[string]string {
	output := map[string]string{}

	if apiResponse == nil || apiResponse.Headers == nil {
		log.Log.Debugf("[R#%d] apiResponse is nil or headers is nil")
		return output
	}

	for key, value := range apiResponse.Headers {
		if string(key[0]) == "X" {
			output[key] = value[0]
		}
	}

	return output
}

func HttpGetHeadersFunctionExecution(jobResult *scheduler.JobResult) map[string]string {
	output := map[string]string{}

	if jobResult == nil {
		return output
	}

	// jobResult has been executed internally, so we have a single time
	if !jobResult.ExternalExecution {
		if jobResult.Timings == nil {
			return output
		}
		// these are treated as lists
		if jobResult.Timings.TotalTime != nil {
			output[utils.HttpHeaderP2PFaaSTotalTimingsList] = fmt.Sprintf("[%f]", *jobResult.Timings.TotalTime)
		}
		if jobResult.Timings.SchedulingTime != nil {
			output[utils.HttpHeaderP2PFaaSSchedulingTimingsList] = fmt.Sprintf("[%f]", *jobResult.Timings.SchedulingTime)
		}
		if jobResult.Timings.ProbingTime != nil {
			output[utils.HttpHeaderP2PFaaSProbingTimingsList] = fmt.Sprintf("[%f]", *jobResult.Timings.ProbingTime)
		}

		// this is always a single value
		if jobResult.Timings.ExecutionTime != nil {
			output[utils.HttpHeaderP2PFaaSExecutionTime] = fmt.Sprintf("%f", *jobResult.Timings.ExecutionTime)
		}
	}

	// jobResult has been executed externally, so we have a list of times
	if jobResult.ExternalExecution {
		hops := len(jobResult.ExternalExecutionInfo.PeersList) - 1
		output[utils.HttpHeaderP2PFaaSExternallyExecuted] = "True"
		output[utils.HttpHeaderP2PFaaSHops] = fmt.Sprintf("%d", hops)

		if len(jobResult.ExternalExecutionInfo.PeersList) == 0 {
			log.Log.Fatalf("Peers list is empty and the jobResult has been executed externally")
		}

		if jobResult.ExternalExecutionInfo.PeersList[0].Timings.ExecutionTime != nil {
			output[utils.HttpHeaderP2PFaaSExecutionTime] = fmt.Sprintf("%f", *jobResult.ExternalExecutionInfo.PeersList[0].Timings.ExecutionTime)
		}

		var ipList []string
		var idList []string
		var probingTimes []float64
		var totalTimes []float64
		var schedulingTimes []float64

		peers := jobResult.ExternalExecutionInfo.PeersList
		for i := len(jobResult.ExternalExecutionInfo.PeersList) - 1; i >= 0; i-- {
			ipList = append(ipList, peers[i].MachineIp)
			idList = append(idList, peers[i].MachineId)

			if peers[i].Timings.ProbingTime != nil {
				probingTimes = append(probingTimes, *peers[i].Timings.ProbingTime)
			} else {
				probingTimes = append(probingTimes, 0.0)
			}

			if peers[i].Timings.TotalTime != nil {
				totalTimes = append(totalTimes, *peers[i].Timings.TotalTime)
			} else {
				totalTimes = append(totalTimes, 0.0)
			}

			if peers[i].Timings.SchedulingTime != nil {
				schedulingTimes = append(schedulingTimes, *peers[i].Timings.SchedulingTime)
			} else {
				schedulingTimes = append(schedulingTimes, 0.0)
			}
		}

		ipListJ, _ := json.Marshal(ipList)
		idListJ, _ := json.Marshal(idList)
		totalTimesJ, _ := json.Marshal(totalTimes)
		schedulingTimesJ, _ := json.Marshal(schedulingTimes)
		probingTimesJ, _ := json.Marshal(probingTimes)

		output[utils.HttpHeaderP2PFaaSPeersListIp] = fmt.Sprintf("%s", string(ipListJ))
		output[utils.HttpHeaderP2PFaaSPeersListId] = fmt.Sprintf("%s", string(idListJ))

		output[utils.HttpHeaderP2PFaaSTotalTimingsList] = fmt.Sprintf("%s", string(totalTimesJ))
		output[utils.HttpHeaderP2PFaaSProbingTimingsList] = fmt.Sprintf("%s", string(probingTimesJ))
		output[utils.HttpHeaderP2PFaaSSchedulingTimingsList] = fmt.Sprintf("%s", string(schedulingTimesJ))
	}

	return output
}

func ReplyWithErrorFromJobResult(w *http.ResponseWriter, errorCode int, jobResult *scheduler.JobResult, message string) {
	finalHeaders := HttpGetHeadersFromFramework()

	// add headers from result
	if jobResult != nil {
		finalHeaders = utils.MapsMerge(
			finalHeaders,
			HttpGetHeadersFromJobResult(jobResult),
		)

		if jobResult.Response != nil {
			finalHeaders = utils.MapsMerge(
				finalHeaders,
				HttpGetHeadersXFromResponse(jobResult.Response),
			)
		}
	}

	utils.HttpAddHeadersToResponse(w, &finalHeaders)

	if message != "" {
		errors.ReplyWithErrorMessage(w, errorCode, message, nil)
	} else {
		errors.ReplyWithError(w, errorCode, nil)
	}
}

func ReplyWithBodyFromJobResult(serviceRequest *types.ServiceRequest, w *http.ResponseWriter, jobResult *scheduler.JobResult) {
	var err error

	// add headers
	finalHeaders := utils.MapsMerge(
		HttpGetHeadersFromFramework(),
		HttpGetHeadersFromJobResult(jobResult),
		HttpGetHeadersXFromResponse(jobResult.Response),
		HttpGetHeadersFunctionExecution(jobResult),
	)
	utils.HttpAddHeadersToResponse(w, &finalHeaders)

	(*w).WriteHeader(jobResult.Response.StatusCode)

	// check if we need to write the body output
	if jobResult.Response.Body != nil && len(jobResult.Response.Body) > 0 {
		log.Log.Debugf("[R#%d,T%s] Job body has length %d, external=%t", serviceRequest.Id, serviceRequest.IdTracing, len(jobResult.Response.Body), jobResult.ExternalExecution)

		var outputBody []byte

		// decode the job output if it has been executed externally, since when a node offload a jobs, the remote note
		// will reply with base64 encoded body
		if jobResult.ExternalExecution {
			outputBody, err = base64.StdEncoding.DecodeString(string(jobResult.Response.Body))
			if err != nil {
				log.Log.Errorf("[R#%d,T%s] Cannot decode job output: %s", serviceRequest.IdTracing, serviceRequest.Id, err)
				return
			}
		} else {
			outputBody = jobResult.Response.Body
		}

		// Write response
		_, err = (*w).Write(outputBody)
		if err != nil {
			log.Log.Errorf("[R#%d,T%s] Cannot write job output: %s", serviceRequest.Id, serviceRequest.IdTracing, err.Error())
			return
		}
	}
}
