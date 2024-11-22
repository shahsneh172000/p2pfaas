/*
 * P2PFaaS - A framework for FaaS Load Balancing
 * Copyright (c) 2019. Gabriele Proietti Mattia <pm.gabriele@outlook.com>
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
	config2 "discovery/config"
	"discovery/db"
	"discovery/errors"
	"discovery/log"
	"encoding/json"
	"io"
	"io/ioutil"
	"net/http"
)

func ConfigurationGet(w http.ResponseWriter, r *http.Request) {
	// if we do not have the machine ip we report 404
	if config2.GetMachineIp() == "" {
		errors.ReplyWithError(w, errors.ConfigurationNotReady)
		return
	}

	config, err := json.Marshal(config2.GetConfigurationDynamicCopy())
	if err != nil {
		log.Log.Errorf("Cannot encode configuration to json")
		errors.ReplyWithError(w, errors.GenericError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	io.WriteString(w, string(config))
}

func ConfigurationSet(w http.ResponseWriter, r *http.Request) {
	currentConfiguration := config2.GetConfigurationDynamicCopy()
	reqBody, _ := ioutil.ReadAll(r.Body)

	var newConfiguration *config2.ConfigurationDynamic
	var err error

	// do the merge with the default configuration or existing
	err = json.Unmarshal(reqBody, &currentConfiguration)
	newConfiguration = currentConfiguration
	if err != nil {
		log.Log.Errorf("Cannot encode passed configuration")
		errors.ReplyWithError(w, errors.GenericError)
		return
	}

	config2.SetMachineId(newConfiguration.MachineId)
	config2.SetMachineIp(newConfiguration.MachineIp)
	config2.SetMachineFogNetId(newConfiguration.MachineGroupName)
	config2.SetInitServers(newConfiguration.InitServers)
	db.AddInitServers(newConfiguration.InitServers)

	// save configuration to file
	err = config2.SaveConfigurationDynamicToConfigFile()
	if err != nil {
		log.Log.Warningf("Cannot save configuration to file %s", config2.GetConfigurationDynamicFilePath())
		w.WriteHeader(500)
		return
	}

	log.Log.Infof("Configuration updated")

	w.WriteHeader(200)
}
