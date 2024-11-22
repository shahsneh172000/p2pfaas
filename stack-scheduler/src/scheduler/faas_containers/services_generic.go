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

package faas_containers

import (
	"io/ioutil"
	"scheduler/log"
	"scheduler/types"
	"scheduler/utils"
)

func GenFunctionExecute(functionName string, payload []byte, contentType string) (*types.FaasApiResponse, error) {
	var res *types.FaasApiResponse
	var err error

	if payload == nil {
		res, err = functionExecuteApiCall(functionName)
	} else {
		res, err = functionExecutePostApiCall(functionName, payload, contentType)
	}

	if err != nil {
		return nil, err
	}
	if res.StatusCode == 404 {
		return res, ErrorFunctionNotFound{}
	}
	if res.StatusCode >= 500 {
		return res, ErrorInternal{string(res.Body)}
	}
	if res.StatusCode < 200 || res.StatusCode >= 300 {
		return res, ErrorGeneric{string(res.Body)}
	}

	return res, nil
}

/*
 * Utils
 */

func functionExecuteApiCall(functionName string) (*types.FaasApiResponse, error) {
	res, err := utils.HttpGet(GetApiFunctionUrl(functionName))
	if err != nil {
		log.Log.Debugf("Cannot create GET request to %s", err.Error(), GetApiFunctionUrl(functionName))
		return nil, err
	}

	body, _ := ioutil.ReadAll(res.Body)
	_ = res.Body.Close()

	response := types.FaasApiResponse{
		Headers:    res.Header,
		Body:       body,
		StatusCode: res.StatusCode,
	}

	return &response, err
}

func functionExecutePostApiCall(functionName string, payload []byte, contentType string) (*types.FaasApiResponse, error) {
	res, err := utils.HttpPost(GetApiFunctionUrl(functionName), payload, contentType)
	if err != nil {
		log.Log.Debugf("Cannot create POST request to %s", err.Error(), GetApiFunctionUrl(functionName))
		return nil, err
	}

	body, _ := ioutil.ReadAll(res.Body)
	_ = res.Body.Close()

	response := types.FaasApiResponse{
		Headers:    res.Header,
		Body:       body,
		StatusCode: res.StatusCode,
	}

	return &response, err
}
