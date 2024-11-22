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

// Package main is the entrypoint of the scheduler service
package main

import (
	"fmt"
	"github.com/gorilla/mux"
	"net/http"
	"os"
	"scheduler/api"
	"scheduler/api/api_monitoring"
	"scheduler/api/api_peer"
	"scheduler/config"
	"scheduler/log"
	"scheduler/queue"
	"scheduler/scheduler"
	"scheduler/service_discovery"
	"strings"
	"sync"
)

import _ "net/http/pprof"

var wg sync.WaitGroup

func main() {
	wg.Add(2)

	// init modules
	config.Start()
	scheduler.Start()
	service_discovery.Start()
	// metrics.Start()

	go worker()
	go server()

	// Check if profiling should be enabled
	if strings.ToLower(os.Getenv(config.EnvProfiling)) == "true" {
		go pprof()
	}

	log.Log.Infof("Started p2p-fog scheduler v" + config.AppVersion)

	wg.Wait()
}

func server() {
	log.Log.Debugf("Starting webserver thread")

	// init api
	router := mux.NewRouter()
	router.HandleFunc("/", api.Hello).Methods("GET", "POST")
	// OpenFaaS APIs
	router.HandleFunc("/system/functions", api.SystemFunctionsGet).Methods("GET")
	router.HandleFunc("/system/functions", api.SystemFunctionsPost).Methods("POST")
	router.HandleFunc("/system/functions", api.SystemFunctionsPut).Methods("PUT")
	router.HandleFunc("/system/functions", api.SystemFunctionsDelete).Methods("DELETE")
	router.HandleFunc("/system/function/{function}", api.SystemFunctionGet).Methods("GET")
	router.HandleFunc("/system/scale-function/{function}", api.SystemScaleFunctionPost).Methods("POST")
	router.HandleFunc("/function/{function}", api.FunctionPost).Methods("POST")
	router.HandleFunc("/function/{function}", api.FunctionGet).Methods("GET")
	// new APIs
	router.HandleFunc("/monitoring/load", api_monitoring.LoadGetLoad).Methods("GET")
	router.HandleFunc("/monitoring/scale-delay/{function}", api_monitoring.ScaleDelay).Methods("GET")
	router.HandleFunc("/peer/function/{function}", api_peer.FunctionExecute).Methods("POST")
	// prometheus
	// router.Handle("/metrics", promhttp.Handler())
	// dev apis
	router.HandleFunc("/configuration", api.GetConfiguration).Methods("GET")
	router.HandleFunc("/configuration/scheduler", api.GetScheduler).Methods("GET")
	// TODO add auth check on configuration APIs
	// if config.Configuration.GetRunningEnvironment() == config.RunningEnvironmentDevelopment {
	router.HandleFunc("/configuration", api.SetConfiguration).Methods("POST")
	router.HandleFunc("/configuration/scheduler", api.SetScheduler).Methods("POST")
	// }

	// dev apis
	if config.GetRunningEnvironment() == config.RunningEnvironmentDevelopment {
		router.HandleFunc("/dev/learning/act", api.LearningDevTestAct).Methods("GET")
		router.HandleFunc("/dev/learning/act_ws", api.LearningDevTestActWs).Methods("GET")
		router.HandleFunc("/dev/learning/train", api.LearningDevTestTrain).Methods("GET")

		router.HandleFunc("/dev/http/get", api.HttpDevGet).Methods("GET")
		router.HandleFunc("/dev/http/post", api.HttpDevPost).Methods("POST")

		router.HandleFunc("/dev/test/parallel", api.TestDevParallelRequests).Methods("GET")
	}

	server := &http.Server{
		Addr:    fmt.Sprintf("0.0.0.0:%d", config.GetListeningPort()),
		Handler: router,
	}
	server.SetKeepAlivesEnabled(false)

	log.Log.Infof("Started listening on %d", config.GetListeningPort())
	err := server.ListenAndServe()

	log.Log.Fatalf("Error while starting server: %s", err)
	wg.Done()
}

func worker() {
	log.Log.Debugf("Starting queue worker thread")
	queue.Looper()
	wg.Done()
}

func pprof() {
	// pprof
	_ = http.ListenAndServe("0.0.0.0:16060", nil)
}
