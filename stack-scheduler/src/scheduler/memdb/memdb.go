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

// Package memdb implements a fast way for in-memory variables.
package memdb

import (
	"scheduler/config"
	"scheduler/log"
	"scheduler/metrics"
	"sync"
)

type Function struct {
	Name             string
	RunningInstances uint
}

type ErrorFunctionNotFound struct{}

func (ErrorFunctionNotFound) Error() string {
	return "Function not found"
}

/*
 * Code
 */

var functions []*Function
var totalRunningFunctions uint = 0

var totalRunningFunctionsOfTypes = make(map[int64]int64) // the number of running tasks according to the type

var requestNumber uint64 = 0
var requestNumberFromPeers uint64 = 0

var mutexRunningFunctions sync.Mutex
var mutexRequestNumber sync.Mutex
var mutexRequestNumberFromPeers sync.Mutex

func GetRunningInstances(functionName string) (uint, error) {
	mutexRunningFunctions.Lock()

	fn := getFunction(functionName, true)
	if fn == nil {
		mutexRunningFunctions.Unlock()
		return 0, ErrorFunctionNotFound{}
	}

	mutexRunningFunctions.Unlock()

	return fn.RunningInstances, nil
}

func SetFunctionRunning(functionName string, functionType int64) error {
	mutexRunningFunctions.Lock()

	log.Log.Debugf("Setting %s as running", functionName)

	fn := getFunction(functionName, true)
	if fn == nil {
		mutexRunningFunctions.Unlock()
		return ErrorFunctionNotFound{}
	}

	fn.RunningInstances += 1
	totalRunningFunctions += 1
	totalRunningFunctionsOfTypeIncrease(functionType)

	// metrics
	metrics.PostStartedExecutingJob()

	mutexRunningFunctions.Unlock()
	return nil
}

func SetFunctionStopped(functionName string, functionType int64) error {
	mutexRunningFunctions.Lock()

	log.Log.Debugf("Setting %s as stopped", functionName)

	fn := getFunction(functionName, false)
	if fn == nil {
		mutexRunningFunctions.Unlock()
		return ErrorFunctionNotFound{}
	}

	fn.RunningInstances -= 1
	totalRunningFunctions -= 1
	totalRunningFunctionsOfTypeDecrease(functionType)

	// metrics
	metrics.PostStoppedExecutingJob()

	mutexRunningFunctions.Unlock()
	return nil
}

func GetTotalRunningFunctions() uint {
	return totalRunningFunctions
}

func GetTotalRunningFunctionsOfType() map[int64]int64 {
	out := make(map[int64]int64)

	mutexRunningFunctions.Lock()
	for index, element := range totalRunningFunctionsOfTypes {
		out[index] = element
	}
	mutexRunningFunctions.Unlock()

	return out
}

func GetFreeRunningSlots() int {
	return int(config.GetRunningFunctionMax()) - int(GetTotalRunningFunctions())
}

// GetNextRequestNumber returns the next id for the request
func GetNextRequestNumber() uint64 {
	mutexRequestNumber.Lock()
	requestNumber++
	n := requestNumber
	mutexRequestNumber.Unlock()
	return n
}

// GetNextRequestNumberFromPeers returns the next id for the request
func GetNextRequestNumberFromPeers() uint64 {
	mutexRequestNumberFromPeers.Lock()
	requestNumberFromPeers++
	n := requestNumberFromPeers
	mutexRequestNumberFromPeers.Unlock()
	return n
}

/*
 * Utils
 */

func getFunction(functionName string, createIfNotExists bool) *Function {
	for _, fn := range functions {
		if fn.Name == functionName {
			return fn
		}
	}

	log.Log.Debugf("%s function not found, creating", functionName)

	if createIfNotExists {
		newFn := Function{
			Name:             functionName,
			RunningInstances: 0,
		}
		functions = append(functions, &newFn)
		return &newFn
	}

	return nil
}

func totalRunningFunctionsOfTypeIncrease(jobType int64) {
	num, exists := totalRunningFunctionsOfTypes[jobType]
	if !exists {
		totalRunningFunctionsOfTypes[jobType] = 1
		return
	}

	totalRunningFunctionsOfTypes[jobType] = num + 1
}

func totalRunningFunctionsOfTypeDecrease(jobType int64) {
	num, exists := totalRunningFunctionsOfTypes[jobType]
	if !exists {
		return
	}

	totalRunningFunctionsOfTypes[jobType] = num - 1
}
