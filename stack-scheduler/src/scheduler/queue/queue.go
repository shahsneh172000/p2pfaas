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

// Package queue implement a producer consumer queue for lossless models.
package queue

import (
	"scheduler/config"
	"scheduler/log"
	"scheduler/memdb"
	"scheduler/metrics"
	"scheduler/types"
	"scheduler/utils"
	"sync"
	"time"
)

var jobsQueue []*QueuedJob
var jobsQueueLength = 0
var jobsQueueLengthOfTypes = make(map[int64]int64)

// implementing N producers fixed N consumers

var mutex sync.Mutex

var jobsSem = make(utils.Semaphore, 0)
var consumersSem = make(utils.Semaphore, config.GetRunningFunctionMax())

func init() {
	// init metrics
	metrics.PostParallelJobsSlots(int(config.GetRunningFunctionMax()))
	metrics.PostQueueSize(int(config.GetQueueLengthMax()))
}

// EnqueueJob enqueues the passed job in the queue and it blocks the caller until the job has been executed
func EnqueueJob(request *types.ServiceRequest) (*QueuedJob, error) {
	mutex.Lock()

	if jobsQueueLength > 0 && jobsQueueLength >= int(config.GetQueueLengthMax()) {
		log.Log.Debugf("[R#%d] Cannot enqueue job %s, queue is full", request.Id, request.ServiceName)
		mutex.Unlock()
		return nil, ErrorFull{}
	}

	// critical section
	sem := make(utils.Semaphore, 0)
	job := &QueuedJob{
		Request:   request,
		Semaphore: &sem,
		Timings: &Timings{
			ExecutionTime:     0.0,
			FaasExecutionTime: 0.0,
			QueueTime:         0.0,
		},
	}

	jobsQueue = append(jobsQueue, job)
	jobsQueueLength += 1
	lengthIncreaseOfType(request.ServiceType)

	log.Log.Debugf("[R#%d] Enqueued job %s", job.Request.Id, job.Request.ServiceName)

	// metrics
	metrics.PostQueueAssignedSlot()

	// end critical section
	mutex.Unlock()

	// add a job
	jobsSem.Signal()

	// start time
	startQueueTime := time.Now()

	// lock until job is completed
	job.Semaphore.Wait(1)

	// stop time
	job.Timings.QueueTime = time.Since(startQueueTime).Seconds()

	return job, nil
}

func dequeueJob() *QueuedJob {
	jobsSem.Wait(1)
	mutex.Lock()

	job := jobsQueue[0]

	if len(jobsQueue) == 1 {
		jobsQueue = []*QueuedJob{}
	} else {
		jobsQueue = jobsQueue[1:]
	}

	jobsQueueLength -= 1
	lengthDecreaseOfType(job.Request.ServiceType)

	// metrics
	metrics.PostQueueFreedSlot()

	mutex.Unlock()
	return job
}

/*
 * Utils
 */

func GetLength() int {
	return jobsQueueLength
}

func GetLengthOfTypes() map[int64]int64 {
	out := make(map[int64]int64)

	mutex.Lock()
	for index, element := range jobsQueueLengthOfTypes {
		out[index] = element
	}
	mutex.Unlock()

	return out
}

/*
 * Internal
 */

func lengthIncreaseOfType(jobType int64) {
	num, exists := jobsQueueLengthOfTypes[jobType]
	if !exists {
		jobsQueueLengthOfTypes[jobType] = 1
		return
	}

	jobsQueueLengthOfTypes[jobType] = num + 1
}

func lengthDecreaseOfType(jobType int64) {
	num, exists := jobsQueueLengthOfTypes[jobType]
	if !exists {
		return
	}

	jobsQueueLengthOfTypes[jobType] = num - 1
}

/*
 * Core
 */

func Looper() {
	for {
		// Block here if we do not have consumers
		consumersSem.Wait(1)
		log.Log.Debugf("Consumer available! Queue has %d jobs in queue and %d running", GetLength(), memdb.GetTotalRunningFunctions())

		// Block here if we do not have jobs
		job := dequeueJob()
		log.Log.Debugf("QueuedJob available! Queue has %d jobs in queue and %d running", GetLength(), memdb.GetTotalRunningFunctions())

		// Execute the job
		go executeNow(job)

		// If job is executed we will release the consumersSem in the executeNow thread
	}
}
