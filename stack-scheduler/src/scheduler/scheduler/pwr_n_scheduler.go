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

package scheduler

import (
	"fmt"
	"scheduler/log"
	"scheduler/memdb"
	"scheduler/queue"
	"scheduler/scheduler_service"
	"scheduler/types"
	"scheduler/utils"
	"time"
)

const PowerOfNSchedulerName = "PowerOfNScheduler"

// PowerOfNScheduler implement the power-of-n choices based scheduler
type PowerOfNScheduler struct {
	// F is the fan-out, that is the number of probed nodes
	F uint
	// T is threshold, that from which number of currently executing tasks the probing to others is started
	T uint
	// Loss tells if tasks are loss when there are no free slots for executing the task in parallel with others
	Loss bool
	// MaxHops is the maximum number of hops that a request can be subjected to before being executed
	MaxHops uint // maximum number of hops
}

func (s PowerOfNScheduler) GetFullName() string {
	return fmt.Sprintf("%s(%d, %d, %t, %d)", PowerOfNSchedulerName, s.F, s.T, s.Loss, s.MaxHops)
}

func (s PowerOfNScheduler) GetScheduler() *types.SchedulerDescriptor {
	return &types.SchedulerDescriptor{
		Name: PowerOfNSchedulerName,
		Parameters: []string{
			fmt.Sprintf("%d", s.F),
			fmt.Sprintf("%d", s.T),
			fmt.Sprintf("%t", s.Loss),
			fmt.Sprintf("%d", s.MaxHops),
		},
	}
}

// Schedule a service request. This call is blocking until the job has been executed locally or externally.
func (s PowerOfNScheduler) Schedule(req *types.ServiceRequest) (*JobResult, error) {
	log.Log.Debugf("Scheduling job %s", req.ServiceName)
	currentRunningFunctions := memdb.GetTotalRunningFunctions()
	currentQueueLength := queue.GetLength()
	currentLoad := currentRunningFunctions + uint(currentQueueLength)

	startedScheduling := time.Now()
	timingsStart := types.TimingsStart{ArrivedAt: &startedScheduling}

	balancingHit := currentLoad >= s.T
	jobMustExecutedHere := req.External && req.ExternalJobRequest.Hops >= int(s.MaxHops)

	log.Log.Debugf("balancingHit %t - jobMustExecutedHere %t", balancingHit, jobMustExecutedHere)

	// check if the balancing condition is hit
	if balancingHit && !jobMustExecutedHere {
		// save time
		startedProbingTime := time.Now()
		timingsStart.ProbingStartedAt = &startedProbingTime
		// get N Random machines and ask them for load and pick the least loaded
		leastLoaded, _, err := scheduler_service.GetLeastLoadedMachineOfNRandom(s.F, currentLoad, !s.Loss, true)
		// save time
		endProbingTime := time.Now()
		timingsStart.ProbingEndedAt = &endProbingTime

		if err != nil {
			log.Log.Debugf("Error in retrieving machines %s", err.Error())
			// no machine less loaded than us, we are obliged to run the job in this machine or discard the job
			// if we cannot handle it
			return executeJobLocally(req, &timingsStart, s.GetFullName())
		}

		return executeJobExternally(req, leastLoaded, &timingsStart, s.GetFullName())
	}

	return executeJobLocally(req, &timingsStart, s.GetFullName())
}

func (s PowerOfNScheduler) addHeadersToResult(result *JobResult, reqId uint64, state []float64, action float64, eps float64) {
	resultHeaders := map[string]string{}
	resultHeaders[utils.HttpHeaderP2PFaaSProbeMessagesTime] = fmt.Sprintf("%d", result.ProbingMessages)
	result.ResponseHeaders = &resultHeaders
}
