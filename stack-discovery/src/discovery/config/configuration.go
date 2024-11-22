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

package config

import (
	"discovery/log"
	"discovery/utils"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"os"
	"strconv"
)

type ConfigurationStatic struct {
	PollTime                          uint   `json:"poll_time" bson:"poll_time"`
	DataPath                          string `json:"data_path" bson:"data_path"`
	ListeningHost                     string `json:"listening_host" bson:"listening_host"`
	ListeningPort                     uint   `json:"listening_port" bson:"listening_port"`
	PollTimeout                       uint   `json:"poll_timeout" bson:"poll_timeout"`
	MachineDeadPollsRemovingThreshold uint   `json:"machine_dead_polls_removing_threshold" bson:"machine_dead_polls_removing_threshold"`
	RunningEnvironment                string `json:"running_environment" bson:"running_environment"`
	DefaultIface                      string `json:"default_iface" bson:"default_iface"`
}

type ConfigurationDynamic struct {
	MachineIp        string   `json:"machine_ip" bson:"machine_ip"`
	MachineId        string   `json:"machine_id" bson:"machine_id"`
	MachineGroupName string   `json:"machine_group_name" bson:"machine_group_name"`
	InitServers      []string `json:"init_servers" bson:"init_servers"`
}

/*
 * Sample configuration file
 *
 * {
 *   "machine_ip": "192.168.99.102",
 *   "machine_id": "p2pfogc2n0",
 *   "init_servers": ["192.168.99.100"]
 * }
 *
 */

type ConfigError struct{}

func (ConfigError) Error() string {
	return "Configuration Error"
}

/*
 * Inits
 */

func InitConfigurationStatic() {
	configurationStatic = GetDefaultConfigurationStatic()

	if envVar := os.Getenv(EnvRunningEnvironment); envVar != "" {
		if envVar == RunningEnvironmentProduction || envVar == RunningEnvironmentDevelopment {
			configurationStatic.RunningEnvironment = envVar
		}
	}

	if envVar := os.Getenv(EnvDataPath); envVar != "" {
		configurationStatic.DataPath = envVar
	}

	if envVar := os.Getenv(EnvListeningHost); envVar != "" {
		configurationStatic.ListeningHost = envVar
	}

	if envVar := os.Getenv(EnvListeningPort); envVar != "" {
		listPort, err := strconv.Atoi(envVar)
		if err == nil && listPort > 0 {
			configurationStatic.ListeningPort = uint(listPort)
		}
	}

	if envVar := os.Getenv(EnvPollTime); envVar != "" {
		listPort, err := strconv.Atoi(envVar)
		if err == nil && listPort > 0 {
			configurationStatic.PollTime = uint(listPort)
		}
	}

	if envVar := os.Getenv(EnvPollTimeout); envVar != "" {
		listPort, err := strconv.Atoi(envVar)
		if err == nil && listPort > 0 {
			configurationStatic.PollTime = uint(listPort)
		}
	}

	// if envVar := os.Getenv(EnvInitServers); envVar != "" {
	//	configurationStatic.InitServers = strings.Split(envVar, ",")
	//}

	if envVar := os.Getenv(EnvDefaultIface); envVar != "" {
		configurationStatic.DefaultIface = envVar
	}

	if envVar := os.Getenv(EnvMachineDeadPollsRemovingThreshold); envVar != "" {
		listPort, err := strconv.Atoi(envVar)
		if err == nil && listPort > 0 {
			configurationStatic.MachineDeadPollsRemovingThreshold = uint(listPort)
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

	if !configurationDynamicReadFromFile {
		err = SaveConfigurationDynamicToConfigFile()
		if err != nil {
			log.Log.Errorf("Cannot save configuration dynamic to file %s", GetConfigurationDynamicFilePath())
		}
	}
}

/*
 * Getters
 */

func GetMachineIp() string {
	return configurationDynamic.MachineIp
}
func GetMachineId() string {
	return configurationDynamic.MachineIp
}
func GetMachineGroupName() string {
	return configurationDynamic.MachineGroupName
}
func GetDataPath() string {
	return configurationStatic.DataPath
}
func GetInitServers() []string {
	return configurationDynamic.InitServers
}
func GetPollTime() uint {
	return configurationStatic.PollTime
}
func GetListeningPort() uint {
	return configurationStatic.ListeningPort
}
func GetListeningHost() string {
	return configurationStatic.ListeningHost
}
func GetPollTimeout() uint {
	return configurationStatic.PollTimeout
}
func GetMachineDeadPollsRemovingThreshold() uint {
	return configurationStatic.MachineDeadPollsRemovingThreshold
}
func GetRunningEnvironment() string {
	return configurationStatic.RunningEnvironment
}
func GetDefaultIface() string {
	return configurationStatic.DefaultIface
}

func GetConfigurationDynamicCopy() *ConfigurationDynamic {
	copiedConf := *configurationDynamic

	return &copiedConf
}

func GetConfigurationStaticString() string {
	confBytes, err := json.Marshal(configurationStatic)
	if err != nil {
		return ""
	}

	return string(confBytes)
}

/*
 * Setters
 */

func SetMachineIp(ip string) {
	configurationDynamic.MachineIp = ip
}
func SetMachineId(id string) {
	configurationDynamic.MachineId = id
}
func SetMachineFogNetId(id string) {
	configurationDynamic.MachineGroupName = id
}
func SetInitServers(servers []string) {
	configurationDynamic.InitServers = servers
}

/*
 * Utils
 */

func ReadConfigurationDynamicFromFile() (*ConfigurationDynamic, error) {
	conf := GetDefaultConfigurationDynamic()

	file, err := ioutil.ReadFile(GetConfigurationDynamicFilePath())
	if err != nil {
		log.Log.Info("Cannot read configuration file at %s", GetConfigurationDynamicFilePath())
		return nil, err
	} else {
		err = json.Unmarshal(file, conf)
		if err != nil {
			log.Log.Errorf("Cannot decode configuration file, maybe not valid json: %s", err.Error())
			return nil, err
		}
	}

	// check fields
	if conf.MachineId == "" || conf.MachineIp == "" {
		log.Log.Warningf("Configuration file does not contain MachineId or MachineIp. Will try to get ip from \"%s\"", GetDefaultIface())
		// get ip from machine
		ip, err := utils.GetInternalIP(GetDefaultIface())
		if err != nil {
			return conf, nil
		}
		conf.MachineIp = ip
		// generate machine id
		conf.MachineId = fmt.Sprintf("p2pfaas-%s", conf.MachineIp)
		log.Log.Infof("Got from machine ip: %s and id: %s", conf.MachineIp, conf.MachineId)
	}

	return conf, nil
}

func GetDefaultConfigurationStatic() *ConfigurationStatic {
	conf := &ConfigurationStatic{
		PollTime:                          DefaultPollTime,
		DataPath:                          DefaultDataPath,
		ListeningHost:                     DefaultListeningHost,
		ListeningPort:                     DefaultListeningPort,
		PollTimeout:                       DefaultPollTimeoutTime,
		MachineDeadPollsRemovingThreshold: DefaultMachineDeadPollsRemovingThreshold,
		DefaultIface:                      DefaultIfaceName,
		RunningEnvironment:                os.Getenv(EnvRunningEnvironment),
	}
	return conf
}

func GetDefaultConfigurationDynamic() *ConfigurationDynamic {
	conf := &ConfigurationDynamic{
		InitServers:      []string{},
		MachineIp:        "",
		MachineId:        "",
		MachineGroupName: "",
	}
	return conf
}
