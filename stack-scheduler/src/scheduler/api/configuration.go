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
	"encoding/json"
	"io/ioutil"
	"net/http"
	"scheduler/config"
	"scheduler/errors"
	"scheduler/log"
	"scheduler/scheduler"
	"scheduler/types"
	"scheduler/utils"
)

// GetConfiguration Retrieve the current configuration of the system.
func GetConfiguration(w http.ResponseWriter, r *http.Request) {
	configuration, err := json.Marshal(config.GetConfigurationDynamicCopy())
	if err != nil {
		log.Log.Errorf("Cannot encode configuration to json")
		errors.ReplyWithError(&w, errors.GenericError, nil)
		return
	}

	utils.HttpSendJSONResponse(&w, 200, string(configuration), nil)
}

// SetConfiguration Set the configuration of the system (conform to config.ConfigurationSetExp) and save it to a file,
// in such a way it is load at the startup. This configuration does not include the scheduler information.
func SetConfiguration(w http.ResponseWriter, r *http.Request) {
	currentConfiguration := config.GetConfigurationDynamicCopy()
	reqBody, _ := ioutil.ReadAll(r.Body)

	var newConfiguration *config.ConfigurationDynamic
	var err error

	// do the merge with the default configuration or existing
	err = json.Unmarshal(reqBody, &currentConfiguration)
	newConfiguration = currentConfiguration
	if err != nil {
		log.Log.Errorf("Cannot encode passed configuration: %s", err)
		errors.ReplyWithError(&w, errors.GenericError, nil)
		return
	}

	config.SetRunningFunctionMax(newConfiguration.ParallelRunningFunctionsMax)
	config.SetQueueLengthMax(newConfiguration.QueueLengthMax)
	config.SetQueueEnabled(newConfiguration.QueueEnabled)

	// save configuration to file
	err = config.SaveConfigurationDynamicToConfigFile()
	if err != nil {
		log.Log.Warningf("Cannot save configuration to file %s", config.GetConfigFilePath())
	}

	log.Log.Infof("Configuration updated")

	w.WriteHeader(200)
}

// GetScheduler Retrieves the scheduler information.
func GetScheduler(w http.ResponseWriter, r *http.Request) {
	sched, err := json.Marshal(scheduler.GetScheduler())
	if err != nil {
		log.Log.Errorf("Cannot encode configuration to json")
		errors.ReplyWithError(&w, errors.GenericError, nil)
		return
	}

	utils.HttpSendJSONResponse(&w, 200, string(sched), nil)
}

// SetScheduler Sets the scheduler information and save the configuration to file in such a way it is loaded automatically at startup.
func SetScheduler(w http.ResponseWriter, r *http.Request) {
	var proposedScheduler = types.SchedulerDescriptor{}
	reqBody, _ := ioutil.ReadAll(r.Body)

	err := json.Unmarshal(reqBody, &proposedScheduler)
	if err != nil {
		log.Log.Errorf("Cannot decode passed configuration: %s", err.Error())
		errors.ReplyWithError(&w, errors.InputNotValid, nil)
		return
	}

	err = scheduler.SetScheduler(&proposedScheduler)
	if err != nil {
		log.Log.Errorf("Cannot set new scheduler: %s", err.Error())
		errors.ReplyWithErrorMessage(&w, errors.GenericError, err.Error(), nil)
		return
	}

	// save configuration to file
	err = config.SaveConfigurationSchedulerToConfigFile(scheduler.GetScheduler())
	if err != nil {
		log.Log.Errorf("Cannot save configuration to file %s", config.GetConfigSchedulerFilePath())
	}

	log.Log.Infof("Configuration updated with scheduler: %s", scheduler.GetName())

	w.WriteHeader(200)
}
