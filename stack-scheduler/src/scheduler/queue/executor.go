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

package queue

import (
	"scheduler/config"
	"scheduler/faas"
	"scheduler/faas_openfaas"
	"scheduler/log"
	"scheduler/memdb"
	"time"
)

// executeNow executes the passed job setting the memdb and unlocking both the job and the consumer semaphores
func executeNow(job *QueuedJob) {
	log.Log.Debugf("%s starting execution, with payload %t and type %s", job.Request.ServiceName, job.Request.Payload != nil, job.Request.PayloadContentType)

	_ = memdb.SetFunctionRunning(job.Request.ServiceName, job.Request.ServiceType)

	startExecutionTime := time.Now()

	res, err := faas.FunctionExecute(job.Request.ServiceName, job.Request.Payload, job.Request.PayloadContentType)

	if err != nil {
		log.Log.Errorf("Cannot execute service %s: %s", job.Request.ServiceName, err.Error())
		job.ErrorExecution = true
	} else {
		log.Log.Debugf("%s function executed", job.Request.ServiceName)

		// save the res
		job.Response = res
		job.Timings.ExecutionTime = time.Since(startExecutionTime).Seconds()
		if config.GetOpenFaasEnabled() {
			job.Timings.FaasExecutionTime = faas_openfaas.GetDurationFromExecuteApiCallResponse(res)
		}
	}

	_ = memdb.SetFunctionStopped(job.Request.ServiceName, job.Request.ServiceType)

	// unlock the http request
	job.Semaphore.Signal()

	// unlock consumers
	consumersSem.Signal()
}
