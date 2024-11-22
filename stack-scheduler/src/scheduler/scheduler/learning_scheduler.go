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
	"scheduler/service_discovery"
	"scheduler/service_learning"
	"scheduler/types"
	"scheduler/utils"
	"strconv"
	"time"
)

const LearningSchedulerName = "LearningScheduler"

const LearningSchedulerHeaderKeyState = "X-P2pfaas-Scheduler-Learning-State"
const LearningSchedulerHeaderKeyAction = "X-P2pfaas-Scheduler-Learning-Action"
const LearningSchedulerHeaderKeyEps = "X-P2pfaas-Scheduler-Learning-Eps"
const LearningSchedulerHeaderKeyEid = "X-P2pfaas-Scheduler-Learning-Eid"

const LearningSchedulerHeaderKeyFps = "X-P2pfaas-Scheduler-Learning-Fps"
const LearningSchedulerHeaderKeyTaskType = "X-P2pfaas-Scheduler-Learning-Task-Type"

// LearningScheduler is a scheduler with makes scheduling decisions based on the Learner service which implements RL models
type LearningScheduler struct {
	// NumberOfTaskTypes is the number of task types which can arrive to the node
	NumberOfTaskTypes uint64
}

func (s LearningScheduler) GetFullName() string {
	return fmt.Sprintf("%s(%d)", LearningSchedulerName, s.NumberOfTaskTypes)
}

func (s LearningScheduler) GetScheduler() *types.SchedulerDescriptor {
	return &types.SchedulerDescriptor{
		Name: LearningSchedulerName,
		Parameters: []string{
			fmt.Sprintf("%d", s.NumberOfTaskTypes),
		},
	}
}

// Schedule a service request. This call is blocking until the job has been executed locally or externally.
func (s LearningScheduler) Schedule(req *types.ServiceRequest) (*JobResult, error) {
	var err error
	var actionRes *service_learning.EntryActOutput
	var targetMachineIp string
	var jobResult *JobResult

	log.Log.Debugf("Scheduling job %s", req.ServiceName)
	now := time.Now()
	timingsStart := types.TimingsStart{ArrivedAt: &now}

	// if request is external, execute it locally
	if req.External {
		return executeJobLocally(req, &timingsStart, s.GetFullName())
	}

	taskType := float64(0)
	// parse the current task type
	taskTypeStr := (*req.Headers)[LearningSchedulerHeaderKeyTaskType]
	if taskTypeStr != "" {
		taskType, err = strconv.ParseFloat(taskTypeStr, 64)
		if err != nil {
			log.Log.Warningf("Cannot parse fps in headers: %s", taskTypeStr)
			taskType = 0
		}
	}
	log.Log.Debugf("Using taskType=%f", taskType)

	// update the service request task type
	req.ServiceType = int64(taskType)

	// prepare the state to be sent to the learner
	mapRunningFunctionsOfType := memdb.GetTotalRunningFunctionsOfType()
	mapQueueLengthOfType := queue.GetLengthOfTypes()
	statesMaps := []map[int64]int64{mapRunningFunctionsOfType, mapQueueLengthOfType}

	state := []float64{taskType}
	totalLoad := int64(0)

	/*
		// state summation of queues
		for i := 0; i < int(s.NumberOfTaskTypes); i++ {
			totalJobs := int64(0)
			for _, stateMap := range statesMaps {
				loadOfState, exists := stateMap[int64(i)]
				if !exists {
					continue
				}
				totalJobs = totalJobs + loadOfState
			}
			state = append(state, float64(totalJobs))
		}
	*/

	// state detailed queues
	for _, stateMap := range statesMaps {
		for i := 0; i < int(s.NumberOfTaskTypes); i++ {
			loadOfState, exists := stateMap[int64(i)]
			if !exists {
				state = append(state, float64(0))
				continue
			}
			totalLoad += loadOfState
			state = append(state, float64(loadOfState))
		}
	}

	actEntry := service_learning.EntryAct{
		State: state,
	}

	// make decision
	actionRes, err = service_learning.SocketAct(&actEntry)
	if err != nil {
		return nil, CannotRetrieveAction{err}
	}

	// actuate the action
	actionInt := int64(actionRes.Action)
	eps := actionRes.Eps

	if actionInt == 0 { // reject
		result := JobResult{TimingsStart: &timingsStart, Scheduler: s.GetFullName()}
		s.addHeadersToResult(&result, req.Id, state, actionRes.Action, eps)

		timingsStart.ScheduledAt = utils.GetTimeNow()
		return &result, JobDeliberatelyRejected{}
	}

	if actionInt == 1 { // execute locally
		timingsStart.ScheduledAt = utils.GetTimeNow()

		jobResult, err = executeJobLocally(req, &timingsStart, s.GetFullName())
		s.addHeadersToResult(jobResult, req.Id, state, actionRes.Action, eps)

		return jobResult, err
	}

	if actionInt == 2 { // probe-and-forward
		// save time
		startedProbingTime := time.Now()
		timingsStart.ProbingStartedAt = &startedProbingTime
		// get N Random machines and ask them for mapRunningFunctionsOfType and pick the least loaded
		leastLoaded, _, err := scheduler_service.GetLeastLoadedMachineOfNRandom(1, uint(totalLoad), true, true)
		// save time
		endProbingTime := time.Now()
		timingsStart.ProbingEndedAt = &endProbingTime

		if err != nil {
			log.Log.Debugf("Error in retrieving machines %s", err.Error())
			// no machine less loaded than us, we are obliged to run the job in this machine or discard the job
			// if we cannot handle it
			jobResult, err = executeJobLocally(req, &timingsStart, s.GetFullName())
			s.addHeadersToResult(jobResult, req.Id, state, actionRes.Action, eps)

			return jobResult, err
		}

		jobResult, err = executeJobExternally(req, leastLoaded, &timingsStart, s.GetFullName())
		s.addHeadersToResult(jobResult, req.Id, state, actionRes.Action, eps)

		return jobResult, err
	}

	// otherwise forward
	targetMachineI := int64(actionRes.Action - 3)
	targetMachineIp, err = service_discovery.GetMachineIpAtIndex(targetMachineI, true)
	if err != nil {
		log.Log.Errorf("Cannot schedule job to machine i=%d of %d: %s", targetMachineI, service_discovery.GetCachedMachineNumber(), err)
		return nil, CannotRetrieveRecipientNode{err}
	}
	log.Log.Debugf("Forwarding to machine %s", targetMachineIp)

	jobResult, err = executeJobExternally(req, targetMachineIp, &timingsStart, s.GetFullName())
	s.addHeadersToResult(jobResult, req.Id, state, actionRes.Action, eps)

	return jobResult, err
}

func (s LearningScheduler) addHeadersToResult(result *JobResult, reqId uint64, state []float64, action float64, eps float64) {
	resultHeaders := map[string]string{}

	resultHeaders[LearningSchedulerHeaderKeyEid] = fmt.Sprintf("%d", reqId)
	resultHeaders[LearningSchedulerHeaderKeyState] = utils.ArrayFloatToStringCommas(state)
	resultHeaders[LearningSchedulerHeaderKeyAction] = fmt.Sprintf("%f", action)
	resultHeaders[LearningSchedulerHeaderKeyEps] = fmt.Sprintf("%f", eps)

	if result != nil {
		result.ResponseHeaders = &resultHeaders
	} else {
		log.Log.Errorf("result is nil, cannot add headers")
	}
}
