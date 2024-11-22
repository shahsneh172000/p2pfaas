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

// Package scheduler implements the core scheduler of the system.
package scheduler

import (
	"encoding/json"
	"io/ioutil"
	"scheduler/config"
	"scheduler/log"
	"scheduler/memdb"
	"scheduler/service_learning"
	"scheduler/types"
	"strconv"
	"time"
)

/*
 * Interfaces
 */

// scheduler defines how a scheduler is made
type scheduler interface {
	// GetFullName used for returning the name of the scheduler with the parameters
	GetFullName() string
	// GetScheduler returns the representation of the scheduler
	GetScheduler() *types.SchedulerDescriptor
	// Schedule a job. This function must be blocking and must return only when the job has been completed, or we cannot
	// schedule it. When this function returns we assume that the client will receive a reply
	Schedule(req *types.ServiceRequest) (*JobResult, error)
}

/*
 * Code
 */

var schedulerCurrent scheduler
var schedulerNoScheduler scheduler
var schedulerForward scheduler
var schedulerReject scheduler

func Start() {

}

func init() {
	log.Log.Infof("Starting initialization of scheduler module")

	useDefault := false
	// try to read the configuration file
	file, err := ioutil.ReadFile(config.GetConfigSchedulerFilePath())
	if err != nil {
		log.Log.Warningf("Could not read the scheduler configuration file at %s, using default", config.GetConfigSchedulerFilePath())
		useDefault = true
	}

	if file != nil {
		log.Log.Debugf("Read file is %s", file)
	}

	var proposedScheduler = types.SchedulerDescriptor{}
	err = json.Unmarshal(file, &proposedScheduler)
	if err != nil {
		log.Log.Warningf("Could not decode scheduler config file, using default")
		useDefault = true
	} else {
		err = SetScheduler(&proposedScheduler)
		if err != nil {
			useDefault = true
		}
	}

	if useDefault {
		schedulerCurrent = getDefaultScheduler()
	} else {
		log.Log.Debugf("Used configuration file")
	}

	// init the no-scheduler
	schedulerNoScheduler = NoSchedulingScheduler{true}
	schedulerForward = ForwardScheduler{1}
	schedulerReject = RejectScheduler{}

	log.Log.Infof("Init with '%s' scheduler", schedulerCurrent.GetFullName())
}

/*
 * Actions
 */

// Schedule schedules a service request with the current set scheduler
func Schedule(req *types.ServiceRequest) (*JobResult, error) {
	return schedulerCurrent.Schedule(req)
}

// ScheduleBypassAlgorithm schedules a service request with the NoScheduler algorithm which always execute locally the function
func ScheduleBypassAlgorithm(req *types.ServiceRequest) (*JobResult, error) {
	return schedulerNoScheduler.Schedule(req)
}

// ScheduleForward schedules a service request with the ForwardScheduler algorithm which always forward the request to a random node
func ScheduleForward(req *types.ServiceRequest) (*JobResult, error) {
	return schedulerForward.Schedule(req)
}

// ScheduleReject schedules a service request with the RejectScheduler algorithm which always reject the request
func ScheduleReject(req *types.ServiceRequest) (*JobResult, error) {
	return schedulerReject.Schedule(req)
}

/*
 * types.SchedulerDescriptor info related
 */

// GetName returns the friendly name of current set scheduler
func GetName() string {
	return schedulerCurrent.GetFullName()
}

// GetScheduler returns the types.SchedulerDescriptor object of current set scheduler
func GetScheduler() *types.SchedulerDescriptor {
	return schedulerCurrent.GetScheduler()
}

// SetScheduler replaces the current scheduler with the passed one
func SetScheduler(sched *types.SchedulerDescriptor) error {
	log.Log.Debugf("Starting setting of scheduler %s", sched)

	if memdb.GetTotalRunningFunctions() != 0 {
		return CannotChangeScheduler{}
	}

	switch sched.Name {

	case NoSchedulingSchedulerName:
		if len(sched.Parameters) < 1 {
			return BadSchedulerParameters{}
		}
		l, err := strconv.ParseBool(sched.Parameters[0])
		if err != nil {
			return BadSchedulerParameters{}
		}
		schedulerCurrent = &NoSchedulingScheduler{Loss: l}
		break

	case ForwardSchedulerName:
		if len(sched.Parameters) < 1 {
			return BadSchedulerParameters{}
		}
		m, err := strconv.ParseUint(sched.Parameters[0], 10, 32)
		if err != nil {
			return BadSchedulerParameters{}
		}
		schedulerCurrent = &ForwardScheduler{
			MaxHops: uint(m),
		}
		break

	case PowerOfNSchedulerName:
		if len(sched.Parameters) < 4 {
			return BadSchedulerParameters{}
		}
		f, err1 := strconv.ParseUint(sched.Parameters[0], 10, 32)
		t, err2 := strconv.ParseUint(sched.Parameters[1], 10, 32)
		l, err3 := strconv.ParseBool(sched.Parameters[2])
		m, err4 := strconv.ParseUint(sched.Parameters[3], 10, 32)
		if err1 != nil || err2 != nil || err3 != nil || err4 != nil {
			return BadSchedulerParameters{}
		}
		schedulerCurrent = &PowerOfNScheduler{
			F:       uint(f),
			T:       uint(t),
			Loss:    l,
			MaxHops: uint(m),
		}
		break

	case PowerOfNSchedulerTauName:
		if len(sched.Parameters) < 5 {
			return BadSchedulerParameters{}
		}
		f, err1 := strconv.ParseUint(sched.Parameters[0], 10, 32)
		T, err2 := strconv.ParseUint(sched.Parameters[1], 10, 32)
		l, err3 := strconv.ParseBool(sched.Parameters[2])
		m, err4 := strconv.ParseUint(sched.Parameters[3], 10, 32)
		t, err5 := time.ParseDuration(sched.Parameters[4]) // duration: 10s, 200ms, etc.
		if err1 != nil || err2 != nil || err3 != nil || err4 != nil || err5 != nil {
			return BadSchedulerParameters{}
		}
		schedulerCurrent = &PowerOfNSchedulerTau{
			F:       uint(f),
			T:       uint(T),
			Loss:    l,
			MaxHops: uint(m),
			Tau:     t,
		}
		break

	case RoundRobinWithMasterSchedulerName:
		if len(sched.Parameters) < 3 {
			return BadSchedulerParameters{}
		}
		m, err1 := strconv.ParseBool(sched.Parameters[0])
		i := sched.Parameters[1]
		l, err2 := strconv.ParseBool(sched.Parameters[2])
		if err1 != nil || err2 != nil {
			return BadSchedulerParameters{}
		}
		schedulerCurrent = &RoundRobinWithMasterScheduler{
			Master:       m,
			MasterIP:     i,
			Loss:         l,
			currentIndex: 0,
		}

	case LearningSchedulerName:
		if len(sched.Parameters) < 1 {
			return BadSchedulerParameters{}
		}

		jobTypes, err := strconv.ParseUint(sched.Parameters[0], 10, 64)
		if err != nil {
			return BadSchedulerParameters{}
		}

		schedulerCurrent = &LearningScheduler{jobTypes}

	default:
		return BadSchedulerParameters{}

	}

	// start the learning module if learning scheduler
	if _, ok := schedulerCurrent.(*LearningScheduler); ok {
		service_learning.Start()
	} else {
		service_learning.Stop()
	}

	return nil
}

func getDefaultScheduler() scheduler {
	/*
		return NoSchedulingScheduler{
			Loss: true,
		}
	*/
	return &PowerOfNScheduler{
		F:       1,
		T:       2,
		Loss:    true,
		MaxHops: 1,
	}
}
