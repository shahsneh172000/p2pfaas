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

package faas_openfaas

import (
	"scheduler/config"
	"scheduler/types"
)

func FunctionsGet() ([]Function, *types.FaasApiResponse, error) {
	return GenFunctionsGet(config.GetOpenFaasListeningHost())
}

func FunctionGet(functionName string) (*Function, *types.FaasApiResponse, error) {
	return GenFunctionGet(config.GetOpenFaasListeningHost(), functionName)
}

func FunctionDeploy(function Function) (*types.FaasApiResponse, error) {
	return GenFunctionDeploy(config.GetOpenFaasListeningHost(), function)
}

func FunctionExecute(functionName string, payload []byte, contentType string) (*types.FaasApiResponse, error) {
	return GenFunctionExecute(config.GetOpenFaasListeningHost(), functionName, payload, contentType)
}

func FunctionScale(functionName string, replicas uint) (*types.FaasApiResponse, error) {
	return GenFunctionScale(config.GetOpenFaasListeningHost(), functionName, replicas)
}

func FunctionScaleByOne(functionName string) (*types.FaasApiResponse, error) {
	return GenFunctionScaleByOne(config.GetOpenFaasListeningHost(), functionName)
}

func FunctionScaleDownByOne(functionName string) (*types.FaasApiResponse, error) {
	return GenFunctionScaleDownByOne(config.GetOpenFaasListeningHost(), functionName)
}
