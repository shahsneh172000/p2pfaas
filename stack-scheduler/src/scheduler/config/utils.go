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
	"scheduler/types"
)

func GetConfigFilePath() string {
	return GetDataPath() + "/" + ConfigurationFileName
}

func GetConfigSchedulerFilePath() string {
	return GetDataPath() + "/" + ConfigurationSchedulerFileName
}

func SaveConfigurationDynamicToConfigFile() error {
	// create folder if not exists
	err := CreateDataFolder() // os.Mkdir(GetDataPath(), 0664)
	if err != nil {
		log.Log.Errorf("Cannot create folder %s: %s", GetDataPath(), err.Error())
		return err
	}

	// save configuration to file
	configJson, err := json.MarshalIndent(configurationDynamic, "", "  ")
	err = os.WriteFile(GetConfigFilePath(), configJson, 0644)
	if err != nil {
		log.Log.Errorf("Cannot save configuration to file %s: %s", GetConfigFilePath(), err.Error())
		return err
	}

	return nil
}

func SaveConfigurationSchedulerToConfigFile(descriptor *types.SchedulerDescriptor) error {
	// create folder if not exists
	err := CreateDataFolder() // os.Mkdir(GetDataPath(), 0664)
	if err != nil {
		log.Log.Errorf("Cannot create folder %s: %s", GetDataPath(), err.Error())
		return err
	}

	// save configuration to file
	configJson, err := json.MarshalIndent(descriptor, "", "  ")
	err = os.WriteFile(GetConfigSchedulerFilePath(), configJson, 0644)
	if err != nil {
		log.Log.Errorf("Cannot save configuration to file %s: %s", GetConfigSchedulerFilePath(), err.Error())
		return err
	}

	return nil
}

func CreateDataFolder() error {
	// check if folder exists
	if _, err := os.Stat(GetDataPath()); !os.IsNotExist(err) {
		return nil
	}

	// create folder if not exists
	err := os.Mkdir(GetDataPath(), 0664)
	if err != nil {
		log.Log.Errorf("Cannot create folder %s: %s", GetDataPath(), err.Error())
		return err
	}

	return nil
}
