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

package check

import (
	"benchmark/log"
	"benchmark/types"
	"benchmark/utils"
	"fmt"
	"io"
	"os"
	"strings"
	"time"
)

func All(params *types.BenchmarkBasicParams, saveResponsesToFile bool) bool {
	res := Benchmarker(params, saveResponsesToFile)
	if !res {
		return res
	}

	res = Scheduler(params, saveResponsesToFile)
	if !res {
		return res
	}

	res = Discovery(params, saveResponsesToFile)
	if !res {
		return res
	}

	res = Learner(params, saveResponsesToFile)
	if !res {
		return res
	}

	return true
}

func Benchmarker(params *types.BenchmarkBasicParams, saveResponsesToFile bool) bool {
	// test if host file exists
	// if !TestFileExists(params.HostsFileDir) {
	//	log.Log.Errorf("Hosts file does not exist")
	//	return false
	//}

	// test if payloads exist
	for _, payloadName := range params.Payloads {
		if !TestFileExists(fmt.Sprintf("%s/%s", params.DirPayloads, payloadName)) {
			log.Log.Errorf("Payload file does not exist: dir=%s name=%s", params.DirPayloads, payloadName)
			return false
		}
	}

	return true
}

func Scheduler(params *types.BenchmarkBasicParams, saveResponsesToFile bool) bool {
	var err error

	// test if configuration is the same
	if responses, ok := TestSameResponseJson(params.Hosts, params.SchedulerPort, "", nil); ok {
		if saveResponsesToFile {
			err = utils.FileSaveStringTo(responses, fmt.Sprintf("%s/%s-scheduler-hello.txt", params.DirLogs, params.TestId))
			if err != nil {
				log.Log.Errorf("Cannot save response to file: %s", err)
			}
		}
	} else {
		log.Log.Errorf("Scheduler configuration not passed")
		return false
	}

	// test if configuration is the same
	if responses, ok := TestSameResponseJson(params.Hosts, params.SchedulerPort, "configuration", nil); ok {
		if saveResponsesToFile {
			err = utils.FileSaveStringTo(responses, fmt.Sprintf("%s/%s-scheduler-configuration.txt", params.DirLogs, params.TestId))
			if err != nil {
				log.Log.Errorf("Cannot save response to file: %s", err)
			}
		}
	} else {
		log.Log.Errorf("Scheduler configuration not passed")
		return false
	}

	// test if configuration/scheduler is the same
	if responses, ok := TestSameResponseJson(params.Hosts, params.SchedulerPort, "configuration/scheduler", nil); ok {
		if saveResponsesToFile {
			err = utils.FileSaveStringTo(responses, fmt.Sprintf("%s/%s-scheduler-configuration-scheduler.txt", params.DirLogs, params.TestId))
			if err != nil {
				log.Log.Errorf("Cannot save response to file: %s", err)
			}
		}
	} else {
		log.Log.Errorf("Scheduler configuration/scheduler not passed")
		return false
	}

	// test if function is 200
	functionUrl := fmt.Sprintf("function/%s", params.FunctionName)
	headers := []utils.HttpHeader{
		{Key: "X-P2pfaas-Scheduler-Bypass", Value: "true"},
	}
	if !TestStatus(params.Hosts, functionUrl, params.SchedulerPort, 200, headers) {
		log.Log.Errorf("Function  configuration not passed")
		return false
	}

	return true
}

func Discovery(params *types.BenchmarkBasicParams, saveResponsesToFile bool) bool {
	// test if /list is the same, contains host number -1
	if !TestResponseSameJsonArrayLength(params.Hosts, params.DiscoveryPort, "list", nil, "alive", len(params.Hosts)-1) {
		log.Log.Errorf("Discovery parameters check not passed for len=%d", len(params.Hosts)-1)
		return false
	}

	return true
}

func Learner(params *types.BenchmarkBasicParams, saveResponsesToFile bool) bool {
	var err error

	// test if versions are the same
	if responses, ok := TestSameResponseJson(params.Hosts, params.LearnerPort, "", nil); ok {
		if saveResponsesToFile {
			err = utils.FileSaveStringTo(responses, fmt.Sprintf("%s/%s-learner-hello.txt", params.DirLogs, params.TestId))
			if err != nil {
				log.Log.Errorf("Cannot save response to file: %s", err)
			}
		}
	} else {
		log.Log.Errorf("Scheduler configuration not passed")
		return false
	}

	// test if parameters are the same
	if responses, ok := TestSameResponseJson(params.Hosts, params.LearnerPort, "learner/parameters", nil); ok {
		if saveResponsesToFile {
			err = utils.FileSaveStringTo(responses, fmt.Sprintf("%s/%s-learner-parameters.txt", params.DirLogs, params.TestId))
			if err != nil {
				log.Log.Errorf("Cannot save response to file: %s", err)
			}
		}
	} else {
		log.Log.Errorf("Scheduler configuration not passed")
		return false
	}

	// reset learner
	if !TestStatus(params.Hosts, "learner/reset", params.LearnerPort, 200, nil) {
		log.Log.Errorf("Learner reset not passed")
		return false
	}

	return true
}

/*
 * Primitives
 */

func TestSameResponseJson(hosts []string, port uint64, url string, headers []utils.HttpHeader) (string, bool) {
	currentRes := ""
	responses := ""

	// do request to every node
	for i, host := range hosts {
		finalUrl := fmt.Sprintf("http://%s:%d/%s", host, port, url)
		startTime := time.Now()

		res, err := utils.HttpGetWithHeaders(finalUrl, headers)
		if err != nil {
			log.Log.Errorf("Cannot perform request to %s", finalUrl)
			return "", false
		}
		endTime := time.Now()

		resBytes, err := io.ReadAll(res.Body)
		resString := string(resBytes)

		responses += fmt.Sprintf("\n=== Response of %s ===\n%s\n\n", finalUrl, resString)

		_ = res.Body.Close()

		if i == 0 {
			currentRes = resString
		}
		if i > 0 && currentRes != resString {
			log.Log.Errorf("url=%s res=%s mismatch!", finalUrl, resString)
			return "", false
		}

		log.Log.Infof("url=%s res=%s time=%f", finalUrl, resString, float64(endTime.Sub(startTime).Microseconds())/1000000.0)
	}

	return responses, true
}

func TestResponseSameJsonArrayLength(hosts []string, port uint64, url string, headers []utils.HttpHeader, keyword string, length int) bool {
	currentResLen := 0
	if length >= 0 {
		currentResLen = length
	}
	// do request to every node
	for i, host := range hosts {
		finalUrl := fmt.Sprintf("http://%s:%d/%s", host, port, url)

		res, err := utils.HttpGetWithHeaders(finalUrl, headers)
		if err != nil {
			log.Log.Errorf("Cannot perform request to %s", finalUrl)
			return false
		}

		resBytes, err := io.ReadAll(res.Body)
		resString := string(resBytes)
		occurrences := strings.Count(resString, keyword)

		_ = res.Body.Close()

		if i == 0 && currentResLen < 0 {
			currentResLen = occurrences
		}
		if i > 0 && currentResLen != occurrences {
			log.Log.Errorf("url=%s res=%d mismatch!", finalUrl, occurrences)
			return false
		}

		log.Log.Infof("url=%s res=%d", finalUrl, occurrences)
	}

	return true
}

func TestStatus(hosts []string, url string, port uint64, status int, headers []utils.HttpHeader) bool {
	// do request to every node
	for _, host := range hosts {
		finalUrl := fmt.Sprintf("http://%s:%d/%s", host, port, url)
		startTime := time.Now()

		res, err := utils.HttpGetWithHeaders(finalUrl, headers)
		if err != nil {
			log.Log.Errorf("Cannot perform request to %s", finalUrl)
			return false
		}

		_ = res.Body.Close()

		endTime := time.Now()

		if res.StatusCode != status {
			log.Log.Errorf("url=%s status=%d mismatch!", finalUrl, res.StatusCode)
			return false
		}

		log.Log.Infof("url=%s res=%d time=%f", finalUrl, res.StatusCode, float64(endTime.Sub(startTime).Microseconds())/1000000.0)
	}

	return true
}

func TestFileExists(filepath string) bool {
	_, err := os.Stat(filepath)
	return !os.IsNotExist(err)
}
