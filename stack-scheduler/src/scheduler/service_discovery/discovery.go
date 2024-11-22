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

// Package service_discovery implements all functions that made possible the communication with the service_discovery service.
//
// The package when init checks if the service_discovery service is available for getting its configuration, if it is not then the
// scheduler is not started and the check is done every 5 seconds.
package service_discovery

import (
	s_config "scheduler/config"
	"scheduler/log"
	"time"
)

func init() {
	// try to get service_discovery configuration
	log.Log.Debugf("Trying to get configuration from service_discovery service")
	for {
		config, err := GetConfiguration()
		if err != nil {
			log.Log.Warningf("Cannot retrieve discovery configuration at %s:%d, retrying in 5 seconds...", s_config.GetServiceDiscoveryListeningHost(), s_config.GetServiceLearningListeningPort())
			time.Sleep(5 * time.Second)
			continue
		}
		Configuration = config
		log.Log.Infof("Init machine as %s (%s) with service_discovery configuration ", Configuration.MachineId, Configuration.MachineIp)
		break
	}
}

func Start() {

}
