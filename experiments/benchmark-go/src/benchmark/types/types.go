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

package types

import "time"

const (
	TrafficGenerationDistributionPoissonString       = "poisson"
	TrafficGenerationDistributionDeterministicString = "deterministic"
)
const (
	TrafficGenerationDistributionPoisson = iota
	TrafficGenerationDistributionDeterministic
)

type BenchmarkBasicParams struct {
	TestId string

	LambdasArray []float64
	LambdaRange  []float64

	DiscoveryPort uint64
	SchedulerPort uint64
	LearnerPort   uint64
	BenchmarkTime uint64

	Hosts        []string
	HostsFileDir string
	FunctionName string

	DirLogs         string
	DirPayloads     string
	DirTrafficModel string

	Payloads              []string
	PayloadMixPercentages []float64

	Learning                bool
	LearningRewardDeadlines []float64
	LearningSetReward       bool
	LearningBatchSize       uint64

	TrafficModelFilenamePrefix    string
	TrafficModelType              string
	TrafficGenerationDistribution int
}

type BenchmarkResult struct {
	NodeId string
	ReqId  int64
	TypeId int64

	RequestsRate float64
	PayloadName  string

	TimestampStart time.Time
	TimestampEnd   time.Time

	TimeTotal     float64
	TimeExecution float64

	TimesProbing    []float64
	TimesScheduling []float64
	TimesService    []float64

	TimesParsed bool

	PeersListIp []string

	DidProbing         bool
	ExternallyExecuted bool
	Hops               int64

	ResponseStatusCode     int64
	ResponseErrorCode      int64
	RequestNetError        uint64
	RequestNetErrorMessage string

	LearningEid     string
	LearningState   string
	LearningAction  string
	LearningEpsilon float64
	LearningReward  float64
	LearningParsed  bool
}

type LearningEntry struct {
	Eid    string  `json:"eid"`
	State  string  `json:"state"`
	Action string  `json:"action"`
	Reward float64 `json:"reward"`
}

type Payload struct {
	Id     int64
	Name   string
	Mime   string
	Binary []byte
}

type ResponseError struct {
	Code    int64  `json:"code"`
	Message string `json:"message"`
}
