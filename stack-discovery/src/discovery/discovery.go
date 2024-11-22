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

// Package main is the entrypoint of the service
package main

import (
	"discovery/api"
	"discovery/config"
	"discovery/db"
	"discovery/log"
	"discovery/watcher"
	"fmt"
	"github.com/gorilla/mux"
	"net/http"
	"sync"
)

var wg sync.WaitGroup

func main() {
	// init modules
	config.Start()
	db.Start()

	wg.Add(2)
	go server()
	go watchd()

	log.Log.Infof("Discovery server started successfully")

	wg.Wait()
}

func server() {
	// init modules
	// db.AddInitServers(config.GetInitServers())

	// init api
	router := mux.NewRouter()
	router.HandleFunc("/", api.Hello).Methods("GET")
	router.HandleFunc("/list", api.ServersGetList).Methods("GET")
	router.HandleFunc("/reset", api.ServersReset).Methods("GET")
	// dev apis
	// if config.Configuration.GetRunningEnvironment() == config.RunningEnvironmentDevelopment {
	// TODO secure these apis
	router.HandleFunc("/configuration", api.ConfigurationGet).Methods("GET")
	router.HandleFunc("/configuration", api.ConfigurationSet).Methods("POST")
	// }

	server := &http.Server{
		Addr:    fmt.Sprintf("%s:%d", config.GetListeningHost(), config.GetListeningPort()),
		Handler: router,
	}

	log.Log.Infof("Started listening on %s:%d", config.GetListeningHost(), config.GetListeningPort())
	err := server.ListenAndServe()

	log.Log.Fatalf("Error while starting server: %s", err)
	wg.Done()
}

func watchd() {
	log.Log.Infof("Watcher started")
	watcher.PollingLooper()
	wg.Done()
}
