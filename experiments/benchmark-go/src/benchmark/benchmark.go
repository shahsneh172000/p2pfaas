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

package main

import (
	"benchmark/check"
	"benchmark/db"
	"benchmark/log"
	"benchmark/profiling"
	"benchmark/suite"
	"benchmark/traffic"
	"benchmark/types"
	"benchmark/utils"
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"os/signal"
	"strings"
	"time"
)

func main() {
	var err error
	fmt.Println("P2PFaaS Parallel Benchmarker")

	/*
		> test_id {test_id}
		> hosts_file_path {hosts_file_path}
		> scheduler_port {scheduler_port}
		> discovery_port {discovery_port}
		> hosts {hosts}
		> function_url {function_url}
		> poisson {poisson}
		> lambda [{start_lambda:.2f}, {end_lambda:.2f}]
		> lambda_delta {lambda_delta:.2f}
		> skip_check {skip_check}
		> dir_log {dir_log}
		> payloads_dir {payloads_dir}
		> payloads_list {payloads_list}
		> requests_rate_array {requests_rate_array}
		> benchmark_time {benchmark_time}
		> learning {learning}
		> learning_reward_deadline {learning_reward_deadline}
	*/

	testId := time.Now().Format("20060102-150405")

	// arrays
	var arrayLambdaS string
	var arrayPayloadsS string
	var arrayLambdaRangeS string
	var arrayMixPayloadsPercentagesS string
	var arrayDeadlinesS string

	var lambdaDelta float64

	var schedulerPort uint64
	var discoveryPort uint64
	var learnerPort uint64
	var skipCheck bool

	var functionName string
	var benchmarkTime uint64
	var learning bool
	var learningSetReward bool
	var learningBatchSize uint64

	// dirs
	var dirLog string
	var dirPayloads string

	// paths
	var filePathHosts string

	// trafficModel
	var trafficModelDir string
	var trafficModelFilenamePrefix string
	var trafficModelFilenameExtension string
	var trafficModelType string
	var trafficModelShift float64
	var trafficModelRepetitions float64
	var trafficModelMinLoad float64
	var trafficModelMaxLoad float64
	var trafficGenerationDistributionS string
	var trafficGenerationDistribution int

	var debug bool

	// flags declaration using flag package
	flag.StringVar(&arrayLambdaS, "lambdas", "", "Specify list of lambdas")
	flag.StringVar(&arrayPayloadsS, "payloads", "", "Specify list of lambdas")
	flag.StringVar(&arrayLambdaRangeS, "lambda-range", "", "Specify list of lambdas")
	flag.StringVar(&arrayMixPayloadsPercentagesS, "payloads-mix-percentages", "", "Specify list of lambdas")
	flag.StringVar(&arrayDeadlinesS, "learning-reward-deadlines", "0.3", "Specify list of lambdas")

	flag.Uint64Var(&schedulerPort, "scheduler-port", 18080, "Specify scheduler port, default is 18080")
	flag.Uint64Var(&discoveryPort, "discovery-port", 19000, "Specify scheduler port, default is 18080")
	flag.Uint64Var(&learnerPort, "learner-port", 19020, "Specify scheduler port, default is 18080")
	flag.Uint64Var(&benchmarkTime, "benchmark-time", 1000, "Specify scheduler port, default is 1000")

	flag.BoolVar(&skipCheck, "skip-check", false, "Specify scheduler port, default is 18080")
	flag.BoolVar(&debug, "debug", false, "Specify if debug logging must be enabled")

	flag.StringVar(&functionName, "function-name", "", "Specify list of lambdas")

	flag.StringVar(&dirLog, "dir-log", "./log", "Specify list of lambdas")
	flag.StringVar(&dirPayloads, "dir-payloads", "./blobs", "Specify list of lambdas")

	flag.StringVar(&filePathHosts, "hosts-file", "", "Specify hosts list file path")

	flag.Float64Var(&lambdaDelta, "lambda-delta", 0.1, "Specify list of lambdas")

	// learning
	flag.BoolVar(&learning, "learning", false, "Specify scheduler port, default is 18080")
	flag.Uint64Var(&learningBatchSize, "learning-batch-size", 10, "Specify the batch size used for learning")
	flag.BoolVar(&learningSetReward, "learning-set-reward", false, "Specify if computing the reward independently from the -learning parameter")

	// traffic model
	flag.StringVar(&trafficModelDir, "traffic-model-dir", "./traffic", "Specify list of lambdas")
	flag.StringVar(&trafficModelFilenamePrefix, "traffic-model-file-prefix", "", "Specify hosts list file path")
	flag.StringVar(&trafficModelFilenameExtension, "traffic-model-file-extension", "", "Specify hosts list file path")
	flag.StringVar(&trafficModelType, "traffic-model-type", "", "Specify hosts list file path")
	flag.StringVar(&trafficGenerationDistributionS, "traffic-generation-distribution", "poisson", "Specify the traffic generation distribution")
	flag.Float64Var(&trafficModelShift, "traffic-model-shift", 0.0, "Specify list of lambdas")
	flag.Float64Var(&trafficModelRepetitions, "traffic-model-repetitions", 1.0, "Specify list of lambdas")
	flag.Float64Var(&trafficModelMinLoad, "traffic-model-min-load", 1.0, "Specify list of lambdas")
	flag.Float64Var(&trafficModelMaxLoad, "traffic-model-max-load", 10.0, "Specify list of lambdas")

	flag.Parse() // after declaring flags we need to call it
	flag.VisitAll(func(f *flag.Flag) {
		log.Log.Debugf("Parsed flag: %s=%s", f.Name, f.Value)
	})

	// parse arrays
	log.Log.Debugf("lambdas=%v", arrayLambdaS)

	arrayPayloads := strings.Split(arrayPayloadsS, ",")

	arrayLambda, err := utils.ParseArrayFloat64FromString(arrayLambdaS)
	if err != nil {
		log.Log.Fatalf("Cannot parse array arrayLambdaS=%s", arrayLambdaS)
	}

	arrayLambdaRange, err := utils.ParseArrayFloat64FromString(arrayLambdaRangeS)
	if err != nil {
		log.Log.Fatalf("Cannot parse array arrayLambdaRangeS=%s", arrayLambdaRangeS)
	}

	arrayDeadlines, err := utils.ParseArrayFloat64FromString(arrayDeadlinesS)
	if err != nil {
		log.Log.Fatalf("Cannot parse array arrayLambdaRangeS=%s", arrayDeadlinesS)
	}

	arrayMixPayloadsPercentages, err := utils.ParseArrayFloat64FromString(arrayMixPayloadsPercentagesS)
	if err != nil {
		log.Log.Fatalf("Cannot parse array arrayMixPayloadsPercentagesS=%s", arrayMixPayloadsPercentagesS)
	}
	if len(arrayMixPayloadsPercentages) > 0 && len(arrayMixPayloadsPercentages) != len(arrayPayloads) {
		log.Log.Fatalf("If you specify lambda mix percentages then you must provide a number of items equal to"+
			" number of payloads and it must sum to 1.0: %v != %v", len(arrayMixPayloadsPercentages), len(arrayPayloads))
	}

	// parse traffic distribution
	if trafficGenerationDistributionS == types.TrafficGenerationDistributionDeterministicString {
		trafficGenerationDistribution = types.TrafficGenerationDistributionDeterministic
	} else {
		trafficGenerationDistribution = types.TrafficGenerationDistributionPoisson
	}

	log.Log.Infof("Welcome to P2PFaaS Parallel Benchmarker")

	// check parameters
	hostsArr, err := utils.ParseArrayStringFromFile(filePathHosts)
	if err != nil {
		log.Log.Fatalf("Cannot parse host list from file")
	}

	// prepare test struct
	params := &types.BenchmarkBasicParams{
		TestId:                        testId,
		LambdasArray:                  arrayLambda,
		LambdaRange:                   arrayLambdaRange,
		DiscoveryPort:                 discoveryPort,
		SchedulerPort:                 schedulerPort,
		LearnerPort:                   learnerPort,
		BenchmarkTime:                 benchmarkTime,
		Hosts:                         hostsArr,
		HostsFileDir:                  filePathHosts,
		FunctionName:                  functionName,
		DirLogs:                       dirLog,
		DirPayloads:                   dirPayloads,
		DirTrafficModel:               trafficModelDir,
		Payloads:                      arrayPayloads,
		PayloadMixPercentages:         arrayMixPayloadsPercentages,
		Learning:                      learning,
		LearningRewardDeadlines:       arrayDeadlines,
		LearningSetReward:             learningSetReward,
		LearningBatchSize:             learningBatchSize,
		TrafficModelFilenamePrefix:    trafficModelFilenamePrefix,
		TrafficModelType:              trafficModelType,
		TrafficGenerationDistribution: trafficGenerationDistribution,
	}

	// create dirs
	if !check.TestFileExists(params.DirLogs) {
		err = os.Mkdir(params.DirLogs, 0755)
		if err != nil {
			log.Log.Fatalf("Cannot create log dir: %s", params.DirLogs)
		}
	} else {
		log.Log.Debugf("Log dir %s exists, not creating", params.DirLogs)
	}

	// check services
	if !check.All(params, true) {
		log.Log.Fatalf("Some check did not pass, exiting")
	}

	// init db
	dbPathName := fmt.Sprintf("%s/%s", params.DirLogs, testId)
	db.Init()

	// save the test description to file
	testDescriptionPath := fmt.Sprintf("%s/%s.txt", params.DirLogs, testId)
	bytes, err := json.MarshalIndent(&params, "", "  ")
	if err != nil {
		log.Log.Fatalf("Cannot marshal test params to string")
	}
	err = utils.FileSaveStringTo(string(bytes), testDescriptionPath)
	if err != nil {
		log.Log.Fatalf("Cannot marshal save params to file: %s", testDescriptionPath)
	}

	// set log level
	log.SetDebug(debug)

	// start signal handler
	go signalHandler(params)

	// parse the traffic model
	var trafficModel traffic.Model
	if trafficModelType == "dynamic" {
		trafficModel = traffic.CreateModelDynamic(
			trafficModelDir,
			trafficModelFilenamePrefix,
			trafficModelFilenameExtension,
			int64(len(params.Hosts)),
			trafficModelMinLoad,
			trafficModelMaxLoad,
			float64(benchmarkTime),
			trafficModelShift,
			trafficModelRepetitions,
		)
	} else if trafficModelType == "static" {
		trafficModel = traffic.CreateModelStatic(arrayLambda)
	}

	// start the test suite
	if trafficModel != nil {
		// init the traffic model
		err = trafficModel.Init()
		if err != nil {
			log.Log.Fatalf("Cannot init the traffic model: %s", err)
		}

		suite.StartBenchmarkMixPayloads(trafficModel, params)
	} else {
		suite.StartBenchmarkLambdaRange(arrayLambdaRange, lambdaDelta, params)
	}

	// wait for all requests to terminate
	log.Log.Infof("Waiting for all threads to terminate...")

	// wait that all threads terminated
	utils.JoinWaitGroup.Wait()

	// close the db
	db.SaveDBToDisk(dbPathName)
	db.Close()

	log.Log.Infof("Benchmark ended")
}

func signalHandler(params *types.BenchmarkBasicParams) {
	signalCh := make(chan os.Signal, 1)
	signal.Notify(signalCh, os.Kill)

	for {
		select {
		case <-signalCh:
			profiling.CreateMemProfile(params)
			log.Log.Errorf("Received SIGKILL profiling memory")
		}
	}

}
