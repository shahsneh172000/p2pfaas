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
	"benchmark/log"
	"bytes"
	"net"
	"net/http"
	"time"
)

const HttpLearnerServiceHeaderKeyTaskType = "X-P2pfaas-Scheduler-Learning-Task-Type"
const HttpLearnerServiceHeaderKeyTaskTracingId = "X-P2pfaas-Scheduler-Task-Tracing-Id"

var httpTransport *http.Transport

func init() {
	httpTransport = &http.Transport{
		ResponseHeaderTimeout: 15 * time.Second,
		// MaxIdleConnsPerHost: 8,
		// MaxIdleConns:        30,
		// IdleConnTimeout:     120,
		DisableKeepAlives: true,
		DialContext: (&net.Dialer{
			Timeout: 5 * time.Second,
			// KeepAlive: 120 * time.Second,
		}).DialContext,
	}
}

/*
 * Useful structs
 */

type ErrorHttpCannotCreateRequest struct{}

func (e ErrorHttpCannotCreateRequest) Error() string {
	return "cannot create http request."
}

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
		return nil, err
	}

	if contentType != "" {
		req.Header.Set("Content-Type", contentType)
	}

	client := &http.Client{Transport: httpTransport}
	res, err := client.Do(req)
	if err != nil {
		log.Log.Errorf("cannot POST to %s: %s", url, err.Error())
		return nil, err
	}

	return res, err
}

func HttpPostJSON(url string, json string) (*http.Response, error) {
	req, err := http.NewRequest("POST", url, bytes.NewBufferString(json))
	if req == nil {
		return nil, ErrorHttpCannotCreateRequest{}
	}
	req.Header.Set("Content-Type", "application/json")

	client := &http.Client{Transport: httpTransport}
	res, err := client.Do(req)
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

	client := &http.Client{Transport: httpTransport}
	res, err := client.Do(req)
	if err != nil {
		log.Log.Errorf("Cannot GET to %s: %s", url, err.Error())
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

	client := &http.Client{Transport: httpTransport}
	res, err := client.Do(req)
	if err != nil {
		log.Log.Debugf("Cannot GET to %s: %s", url, err.Error())
	}

	return res, err
}

func HttpPostWithHeaders(url string, payload []byte, contentType string, headers []HttpHeader) (*http.Response, error) {
	req, err := http.NewRequest("POST", url, bytes.NewBuffer(payload))
	if err != nil {
		return nil, err
	}

	if contentType != "" {
		req.Header.Set("Content-Type", contentType)
	}

	// set the headers
	for _, h := range headers {
		req.Header.Add(h.Key, h.Value)
	}

	client := &http.Client{Transport: httpTransport}
	res, err := client.Do(req)
	if err != nil {
		log.Log.Errorf("cannot POST to %s: %s", url, err.Error())
	}

	return res, err
}
