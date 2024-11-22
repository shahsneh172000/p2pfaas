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

package utils

import (
	"bytes"
	"io"
	"net/http"
	"scheduler/config"
	"scheduler/log"
)

const HttpHeaderP2PFaaSVersion = "X-P2pfaas-Version"
const HttpHeaderP2PFaaSScheduler = "X-P2pfaas-Scheduler"
const HttpHeaderP2PFaaSTotalTime = "X-P2pfaas-Timing-Total-Time-Seconds"
const HttpHeaderP2PFaaSExecutionTime = "X-P2pfaas-Timing-Execution-Time-Seconds"
const HttpHeaderP2PFaaSProbingTime = "X-P2pfaas-Timing-Probing-Time-Seconds"
const HttpHeaderP2PFaaSSchedulingTime = "X-P2pfaas-Timing-Scheduling-Time-Seconds"
const HttpHeaderP2PFaaSProbeMessagesTime = "X-P2pfaas-Timing-Probe-Messages"
const HttpHeaderP2PFaaSExternallyExecuted = "X-P2pfaas-Externally-Executed"
const HttpHeaderP2PFaaSHops = "X-P2pfaas-Hops"
const HttpHeaderP2PFaaSPeersListIp = "X-P2pfaas-Peers-List-Ip"
const HttpHeaderP2PFaaSPeersListId = "X-P2pfaas-Peers-List-Id"

const HttpHeaderP2PFaaSTotalTimingsList = "X-P2pfaas-Timing-Total-Seconds-List"
const HttpHeaderP2PFaaSProbingTimingsList = "X-P2pfaas-Timing-Probing-Seconds-List"
const HttpHeaderP2PFaaSSchedulingTimingsList = "X-P2pfaas-Timing-Scheduling-Seconds-List"

// HttpHeaderP2PFaaSSchedulerBypass when set to request will always schedule the request internally
const HttpHeaderP2PFaaSSchedulerBypass = "X-P2pfaas-Scheduler-Bypass"

// HttpHeaderP2PFaaSSchedulerForward when set to request will always forward the request to a random neighbour
const HttpHeaderP2PFaaSSchedulerForward = "X-P2pfaas-Scheduler-Forward"

// HttpHeaderP2PFaaSSchedulerReject when set to request will always reject the request
const HttpHeaderP2PFaaSSchedulerReject = "X-P2pfaas-Scheduler-Reject"

const HttpHeaderP2PFaaSSchedulerTracingId = "X-P2pfaas-Scheduler-Task-Tracing-Id"

type ErrorHttpCannotCreateRequest struct{}

func (e ErrorHttpCannotCreateRequest) Error() string {
	return "cannot create http request."
}

/*
 * Useful structs
 */

type HttpHeader struct {
	Key   string
	Value string
}

/*
 * Generic Http methods
 */

func HttpPost(url string, payload []byte, contentType string) (*http.Response, error) {
	req, err := http.NewRequest("POST", url, bytes.NewBuffer(payload))
	if err != nil {
		return nil, ErrorHttpCannotCreateRequest{}
	}

	if contentType != "" {
		req.Header.Set("Content-Type", contentType)
	}

	res, err := httpClient.Do(req)
	if err != nil {
		log.Log.Debugf("cannot POST to %s: %s", url, err.Error())
	}

	return res, err
}

func HttpPostJSON(url string, json string) (*http.Response, error) {
	req, err := http.NewRequest("POST", url, bytes.NewBufferString(json))
	if req == nil {
		return nil, ErrorHttpCannotCreateRequest{}
	}
	req.Header.Set("Content-Type", "application/json")

	res, err := httpClient.Do(req)
	if err != nil {
		log.Log.Debugf("Cannot POST to %s: %s", url, err.Error())
	}

	return res, err
}

func HttpGet(url string) (*http.Response, error) {
	req, err := http.NewRequest("GET", url, nil)
	if req == nil {
		return nil, ErrorHttpCannotCreateRequest{}
	}

	res, err := httpClient.Do(req)
	if err != nil {
		log.Log.Debugf("Cannot GET to %s: %s", url, err.Error())
	}

	return res, err
}

func HttpGetWithHeaders(url string, headers []HttpHeader) (*http.Response, error) {
	req, err := http.NewRequest("GET", url, nil)
	if req == nil {
		return nil, ErrorHttpCannotCreateRequest{}
	}

	// set the headers
	for _, h := range headers {
		req.Header.Add(h.Key, h.Value)
	}

	res, err := httpClient.Do(req)
	if err != nil {
		log.Log.Debugf("Cannot GET to %s: %s", url, err.Error())
	}

	return res, err
}

// HttpMachineGet performs and http get setting as user agent Machine
func HttpMachineGet(url string) (*http.Response, error) {
	req, err := http.NewRequest("GET", url, nil)
	if req == nil {
		return nil, ErrorHttpCannotCreateRequest{}
	}

	req.Header.Add("User-Agent", config.UserAgentMachine)

	res, err := httpClient.Do(req)
	if err != nil {
		log.Log.Debugf("Cannot GET to %s: %s", url, err.Error())
	}

	return res, err
}

func HttpMachinePostJSON(url string, json string) (*http.Response, error) {
	req, err := http.NewRequest("POST", url, bytes.NewBufferString(json))
	if req == nil {
		return nil, ErrorHttpCannotCreateRequest{}
	}

	req.Header.Set("Content-Type", "application/json")
	req.Header.Add("User-Agent", config.UserAgentMachine)

	res, err := httpClient.Do(req)
	if err != nil {
		log.Log.Debugf("Cannot POST to %s: %s", url, err.Error())
	}

	return res, err
}

func HttpMachinePostJSONWithHeaders(url string, json string, headers *[]HttpHeader) (*http.Response, error) {
	req, err := http.NewRequest("POST", url, bytes.NewBufferString(json))
	if req == nil {
		return nil, ErrorHttpCannotCreateRequest{}
	}

	req.Header.Set("Content-Type", "application/json")
	req.Header.Add("User-Agent", config.UserAgentMachine)

	// set the headers
	if headers != nil {
		for _, h := range *headers {
			req.Header.Add(h.Key, h.Value)
		}
	}
	
	res, err := httpClient.Do(req)
	if err != nil {
		log.Log.Debugf("Cannot POST to %s: %s", url, err.Error())
	}

	return res, err
}

/*
* Utils
 */

func HttpSendJSONResponse(w *http.ResponseWriter, code int, body string, customHeaders *map[string]string) {
	(*w).Header().Set("Content-Type", "application/json")
	HttpAddHeadersToResponse(w, customHeaders)

	(*w).WriteHeader(code)

	_, err := io.WriteString(*w, body)
	if err != nil {
		log.Log.Debugf("Cannot send response: %s", err.Error())
	}
}

func HttpSendJSONResponseByte(w *http.ResponseWriter, code int, body []byte, customHeaders *map[string]string) {
	(*w).Header().Set("Content-Type", "application/json")
	HttpAddHeadersToResponse(w, customHeaders)

	(*w).WriteHeader(code)

	_, err := (*w).Write(body)
	if err != nil {
		log.Log.Debugf("Cannot send response: %s", err.Error())
	}
}

func HttpAddHeadersToResponse(w *http.ResponseWriter, customHeaders *map[string]string) {
	if customHeaders == nil {
		return
	}

	for key, value := range *customHeaders {
		(*w).Header().Set(key, value)
	}
}

func HttpParseXHeaders(headers http.Header) *map[string]string {
	outputHeaders := map[string]string{}

	for key, value := range headers {
		if string(key[0]) == "X" {
			outputHeaders[key] = value[0]
		}
	}

	return &outputHeaders
}
