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

// Package config implements configuration of the service
package config

import (
	"discovery/log"
)

const Version = "0.0.4b"

const DataPath = "/data"
const ConfigurationFileName = "p2p_faas-discovery.json"

const GetParamIp = "p2pfaas-machine-ip"
const GetParamName = "p2pfaas-machine-name"
const GetParamGroupName = "p2pfaas-machine-group-name"

const DefaultDataPath = "/data"
const DefaultListeningHost = "0.0.0.0"
const DefaultListeningPort = 19000
const DefaultPollTime = 120      // seconds
const DefaultPollTimeoutTime = 5 // seconds
const DefaultIfaceName = "eth0"

// DefaultMachineDeadPollsRemovingThreshold tells the number of times we need to poll the machine for removing it from the db
const DefaultMachineDeadPollsRemovingThreshold = 20

const EnvRunningEnvironment = "P2PFAAS_DEV_ENV"
const EnvInitServers = "P2PFAAS_INIT_SERVERS"
const EnvDataPath = "P2PFAAS_DATA_PATH"
const EnvPollTime = "P2PFAAS_POLL_TIME"
const EnvListeningHost = "P2PFAAS_LISTENING_HOST"
const EnvListeningPort = "P2PFAAS_LISTENING_PORT"
const EnvPollTimeout = "P2PFAAS_POLL_TIMEOUT"
const EnvMachineDeadPollsRemovingThreshold = "P2PFAAS_MACHINE_DEAD_POLLS_THRESHOLD"
const EnvDefaultIface = "P2PFAAS_DEFAULT_IFACE"

const RunningEnvironmentProduction = "production"
const RunningEnvironmentDevelopment = "development"

// Configuration general parsed configuration
var configurationDynamic *ConfigurationDynamic
var configurationDynamicReadFromFile = false

var configurationStatic *ConfigurationStatic

func init() {
	InitConfigurationStatic()
	InitConfigurationDynamic()

	log.Log.Info("Starting in %s environment", GetRunningEnvironment())
	log.Log.Infof("Init with %s", GetConfigurationStaticString())
	log.Log.Infof("Init with MachineIp=%s, MachineId=%s, MachineGroupName=%s, loadedFromFile=%t",
		GetMachineIp(), GetMachineId(), GetMachineGroupName(), configurationDynamicReadFromFile)
}

func Start() {

}
