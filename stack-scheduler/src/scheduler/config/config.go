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

// Package config implements all the configuration parameters of the system and their handling.
package config

import (
	"io/ioutil"
	"scheduler/log"
	"strings"
)

const AppName = "p2pfaas-scheduler"
const AppVersion = "0.3.0b"
const AppVersionCommit = "xxx"

const DataPath = "/data"

// const ConfigurationFilePath = "/config"
const ConfigurationFileName = "p2p_faas-scheduler.json"
const ConfigurationSchedulerFileName = "p2p_faas-scheduler-config.json"

// const ConfigurationFileFullPath = ConfigurationFilePath + "/" + ConfigurationFileName
// const SchedulerConfigurationFullPath = ConfigurationFilePath + "/" + SchedulerConfigurationFileName

const DefaultListeningPort = 18080
const DefaultQueueLengthMax = 100
const DefaultFunctionsRunningMax = 10
const DefaultRunningEnvironment = RunningEnvironmentProduction

// env
const EnvRunningEnvironment = "P2PFAAS_DEV_ENV"
const EnvServiceDiscoveryListeningHost = "P2PFAAS_SERVICE_DISCOVERY_HOST"
const EnvServiceDiscoveryListeningPort = "P2PFAAS_SERVICE_DISCOVERY_PORT"
const EnvServiceLearningListeningHost = "P2PFAAS_SERVICE_LEARNING_HOST"
const EnvServiceLearningListeningPort = "P2PFAAS_SERVICE_LEARNING_PORT"
const EnvOpenFaasEnabled = "P2PFAAS_OPENFAAS_ENABLED"
const EnvOpenFaasListeningHost = "P2PFAAS_OPENFAAS_HOST"
const EnvOpenFaasListeningPort = "P2PFAAS_OPENFAAS_PORT"
const EnvFunctionsList = "P2PFAAS_FNS_LIST"
const EnvDataPath = "P2PFAAS_DATA_PATH"

const EnvProfiling = "P2PFAAS_PROF"

const DefaultServiceDiscoveryListeningHost = "discovery"
const DefaultServiceDiscoveryListeningPort = 19000

const DefaultServiceLearningListeningHost = "learner"
const DefaultServiceLearningListeningPort = 19020

const RunningEnvironmentProduction = "production"
const RunningEnvironmentDevelopment = "development"

const DefaultOpenFaaSListeningHost = "faas_containers-openfaas-swarm"
const DefaultOpenFaaSListeningPort = 8080

const DefaultDataPath = "/data"

const UserAgentMachine = "Machine"

/*
 * Variables
 */

var OpenFaaSUsername = "admin"
var OpenFaaSPassword = "admin"

var configurationStatic *ConfigurationStatic
var configurationDynamic *ConfigurationDynamic

var configurationDynamicReadFromFile = false

func init() {
	// init both configurations
	InitConfigurationStatic()
	InitConfigurationDynamic()

	// get the secrets for accessing OpenFaas APIs
	// if os.Getenv(EnvDevelopmentEnvironment) == Configuration.GetRunningEnvironment() {
	log.Log.Infof("Starting in %s environment", GetRunningEnvironment())

	if GetOpenFaasEnabled() {
		username, _ := ioutil.ReadFile("/run/secrets/basic-auth-user")
		OpenFaaSUsername = strings.TrimSpace(string(username))
		password, _ := ioutil.ReadFile("/run/secrets/basic-auth-password")
		OpenFaaSPassword = strings.TrimSpace(string(password))
	}

	// }

	// log.Log.Debug("Init with user %s and password %s", OpenFaaSUsername, OpenFaaSPassword)
	log.Log.Infof("Init with RunningFunctionsMax %d, QueueMaxLength %d, QueueEnabled %v",
		GetRunningFunctionMax(), GetQueueLengthMax(), GetQueueEnabled())
	// log.Log.Infof("Init with functions=%v", GetFunctionsList())
}

func Start() {

}
