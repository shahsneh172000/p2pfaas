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

package config

import (
	"encoding/json"
	"os"
	"scheduler/log"
	"strconv"
	"strings"
)

type ConfigError struct{}

func (ConfigError) Error() string {
	return "Configuration Error"
}

type ConfigurationStatic struct {
	listeningPort                 uint
	serviceDiscoveryListeningPort uint
	serviceDiscoveryListeningHost string
	serviceLearningListeningPort  uint
	serviceLearningListeningHost  string
	runningEnvironment            string
	profilingEnabled              bool
	dataPath                      string

	openFaasEnabled       bool
	openFaasListeningPort uint
	openFaasListeningHost string

	fnList []string
}

type ConfigurationDynamic struct {
	ParallelRunningFunctionsMax uint `json:"parallel_running_functions_max" bson:"parallel_running_functions_max"`
	QueueLengthMax              uint `json:"queue_length_max" bson:"queue_length_max"`
	QueueEnabled                bool `json:"queue_enabled" bson:"queue_enabled"`
}

/*
 * Getters
 */

func IsConfigurationDynamicReadFromFile() bool {
	return configurationDynamicReadFromFile
}

func GetRunningFunctionMax() uint {
	return configurationDynamic.ParallelRunningFunctionsMax
}
func GetQueueLengthMax() uint {
	return configurationDynamic.QueueLengthMax
}
func GetQueueEnabled() bool {
	return configurationDynamic.QueueEnabled
}
func GetListeningPort() uint {
	return configurationStatic.listeningPort
}
func GetDataPath() string {
	return configurationStatic.dataPath
}
func GetOpenFaasEnabled() bool {
	return configurationStatic.openFaasEnabled
}
func GetOpenFaasListeningPort() uint {
	return configurationStatic.openFaasListeningPort
}
func GetOpenFaasListeningHost() string {
	return configurationStatic.openFaasListeningHost
}
func GetServiceDiscoveryListeningPort() uint {
	return configurationStatic.serviceDiscoveryListeningPort
}
func GetServiceDiscoveryListeningHost() string {
	return configurationStatic.serviceDiscoveryListeningHost
}
func GetServiceLearningListeningPort() uint {
	return configurationStatic.serviceLearningListeningPort
}
func GetServiceLearningListeningHost() string {
	return configurationStatic.serviceLearningListeningHost
}
func GetRunningEnvironment() string {
	return configurationStatic.runningEnvironment
}
func IsRunningEnvironmentDevelopment() bool {
	// if not already initialized
	if configurationStatic == nil {
		return true
	}
	return configurationStatic.runningEnvironment == RunningEnvironmentDevelopment
}

// GetFunctionsList is currently unused!
func GetFunctionsList() []string {
	return configurationStatic.fnList
}

func GetConfigurationDynamicCopy() *ConfigurationDynamic {
	copiedConf := *configurationDynamic

	return &copiedConf
}

/*
 * Setters
 */

func SetRunningFunctionMax(n uint) {
	configurationDynamic.ParallelRunningFunctionsMax = n
}
func SetQueueLengthMax(n uint) {
	configurationDynamic.QueueLengthMax = n
}
func SetQueueEnabled(b bool) {
	configurationDynamic.QueueEnabled = b
}

/*
 * Inits
 */

// InitConfigurationStatic prepares and inits the static configuration by loading it from env vars.
func InitConfigurationStatic() {
	configurationStatic = GetDefaultConfigurationStatic()

	if envVar := os.Getenv(EnvRunningEnvironment); envVar != "" {
		if envVar == RunningEnvironmentProduction || envVar == RunningEnvironmentDevelopment {
			configurationStatic.runningEnvironment = envVar
		}
	}

	if envVar := os.Getenv(EnvServiceDiscoveryListeningHost); envVar != "" {
		configurationStatic.serviceDiscoveryListeningHost = envVar
	}

	if envVar := os.Getenv(EnvServiceDiscoveryListeningPort); envVar != "" {
		listPort, err := strconv.Atoi(envVar)
		if err == nil && listPort > 0 {
			configurationStatic.serviceDiscoveryListeningPort = uint(listPort)
		}
	}

	if envVar := os.Getenv(EnvDataPath); envVar != "" {
		configurationStatic.dataPath = envVar
	}

	if envVar := os.Getenv(EnvServiceLearningListeningHost); envVar != "" {
		configurationStatic.serviceLearningListeningHost = envVar
	}

	if envVar := os.Getenv(EnvServiceLearningListeningPort); envVar != "" {
		listPort, err := strconv.Atoi(envVar)
		if err == nil && listPort > 0 {
			configurationStatic.serviceLearningListeningPort = uint(listPort)
		}
	}

	if envVar := os.Getenv(EnvOpenFaasEnabled); envVar != "" {
		enabled, err := strconv.ParseBool(envVar)
		if err == nil {
			configurationStatic.openFaasEnabled = enabled
		}
	}

	if envVar := os.Getenv(EnvOpenFaasListeningHost); envVar != "" {
		configurationStatic.openFaasListeningHost = envVar
	}

	if envVar := os.Getenv(EnvOpenFaasListeningPort); envVar != "" {
		listPort, err := strconv.Atoi(envVar)
		if err == nil && listPort > 0 {
			configurationStatic.openFaasListeningPort = uint(listPort)
		}
	}

	if envVar := os.Getenv(EnvFunctionsList); envVar != "" {
		configurationStatic.fnList = strings.Split(envVar, ",")
	}

	if envVar := os.Getenv(EnvProfiling); envVar != "" {
		enabled, err := strconv.ParseBool(envVar)
		if err == nil {
			configurationStatic.profilingEnabled = enabled
		}
	}

}

// InitConfigurationDynamic prepare the configuration object, returns if config is read from file
func InitConfigurationDynamic() {
	configurationDynamic = GetDefaultConfigurationDynamic()

	// try to read the dynamic from file
	newConf, err := ReadConfigurationDynamicFromFile()
	if err == nil {
		configurationDynamic = newConf
		configurationDynamicReadFromFile = true
	}
}

/*
 * Utils
 */

// ReadConfigurationDynamicFromFile reads the configuration from a file
func ReadConfigurationDynamicFromFile() (*ConfigurationDynamic, error) {
	conf := GetDefaultConfigurationDynamic()

	file, err := os.ReadFile(GetConfigFilePath())
	if IsRunningEnvironmentDevelopment() {
		log.Log.Debugf("Read config file=%s", string(file))
	}
	if err != nil {
		log.Log.Warning("Cannot read configuration file at %s", GetConfigFilePath())
	} else {
		err = json.Unmarshal(file, &conf)
		if err != nil {
			log.Log.Errorf("Cannot decode configuration file, maybe not valid json: %s", err.Error())
			return nil, err
		}
	}

	return conf, nil
}

// GetDefaultConfigurationDynamic returns the dynamic configuration object with default values
func GetDefaultConfigurationDynamic() *ConfigurationDynamic {
	return &ConfigurationDynamic{
		ParallelRunningFunctionsMax: 4,
		QueueLengthMax:              4, // put always > 0
		QueueEnabled:                true,
	}
}

// GetDefaultConfigurationStatic returns the static configuration object with default values
func GetDefaultConfigurationStatic() *ConfigurationStatic {
	return &ConfigurationStatic{
		listeningPort:                 DefaultListeningPort,
		serviceDiscoveryListeningPort: DefaultServiceDiscoveryListeningPort,
		serviceDiscoveryListeningHost: DefaultServiceDiscoveryListeningHost,
		serviceLearningListeningPort:  DefaultServiceLearningListeningPort,
		serviceLearningListeningHost:  DefaultServiceLearningListeningHost,
		dataPath:                      DefaultDataPath,
		runningEnvironment:            DefaultRunningEnvironment,
		openFaasEnabled:               false,
		openFaasListeningPort:         DefaultOpenFaaSListeningPort,
		openFaasListeningHost:         DefaultOpenFaaSListeningHost,
		fnList:                        []string{},
		profilingEnabled:              false,
	}
}
