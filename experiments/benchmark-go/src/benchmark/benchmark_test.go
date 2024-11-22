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
	"benchmark/suite"
	"benchmark/types"
	"testing"
	"time"
)

func TestBenchmarkLambdasArrayMixPayloads(t *testing.T) {
	params := &types.BenchmarkBasicParams{
		TestId:        time.Now().Format("20060102-150405"),
		LambdasArray:  []float64{2, 4, 6, 8, 10, 12, 16, 18, 20, 22, 26, 30},
		LambdaRange:   []float64{},
		DiscoveryPort: 19000,
		SchedulerPort: 18080,
		LearnerPort:   19020,
		BenchmarkTime: 300,
		Hosts: []string{
			"192.168.50.100",
			"192.168.50.101",
			"192.168.50.102",
			"192.168.50.103",
			"192.168.50.104",
			"192.168.50.105",
			"192.168.50.106",
			"192.168.50.107",
			"192.168.50.110",
			"192.168.50.111",
			"192.168.50.112",
			"192.168.50.113",
		},
		HostsFileDir:            "./hosts.txt",
		FunctionName:            "fn-pigo",
		DirLogs:                 "../../scripts/log",
		DirPayloads:             "../../scripts/blobs",
		Payloads:                []string{"familyr_320p.jpg", "familyr_100p.jpg"},
		Learning:                true,
		PayloadMixPercentages:   []float64{0.3, 0.7},
		LearningRewardDeadlines: []float64{0.2, 0.07},
		LearningSetReward:       true,
		LearningBatchSize:       20,
	}

	log.SetDebug(true)

	// check
	if !check.All(params, false) {
		log.Log.Fatalf("Some check did not pass, exiting")
	}

	// init db
	// dbPath := fmt.Sprintf("%s/%s.db", params.DirLogs, params.TestId)
	db.Init()

	suite.StartBenchmarkMixPayloads(params.LambdasArray, params)
}

func testBenchmarkLambdasArraySinglePayload(t *testing.T) {
	params := &types.BenchmarkBasicParams{
		TestId:        time.Now().Format("20060102-150405"),
		LambdasArray:  []float64{2, 4, 6, 8, 10, 12, 16, 18, 20, 22, 26, 30},
		LambdaRange:   []float64{},
		DiscoveryPort: 19000,
		SchedulerPort: 18080,
		LearnerPort:   19020,
		BenchmarkTime: 100,
		Hosts: []string{
			"192.168.50.100",
			"192.168.50.101",
			"192.168.50.102",
			"192.168.50.103",
			"192.168.50.104",
			"192.168.50.105",
			"192.168.50.106",
			"192.168.50.107",
			"192.168.50.110",
			"192.168.50.111",
			"192.168.50.112",
			"192.168.50.113",
		},
		HostsFileDir:            "./hosts.txt",
		FunctionName:            "fn-pigo",
		DirLogs:                 "../../scripts/log",
		DirPayloads:             "../../scripts/blobs",
		Payloads:                []string{"familyr_320p.jpg"},
		Learning:                true,
		LearningRewardDeadlines: []float64{0.2},
		PayloadMixPercentages:   []float64{1.0},
		LearningSetReward:       true,
		LearningBatchSize:       20,
	}

	// check
	if !check.All(params, false) {
		log.Log.Fatalf("Some check did not pass, exiting")
	}

	// init db
	// dbPath := fmt.Sprintf("%s/%s.db", params.DirLogs, params.TestId)
	db.Init()

	suite.StartBenchmarkLambdaArrayMultiPayload(params.LambdasArray, params)
}
