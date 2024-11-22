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
	"scheduler/log"
	"scheduler/types"
	"time"
)

const RejectSchedulerSchedulerName = "RejectScheduler"

// RejectScheduler is a scheduler which rejects all the tasks
type RejectScheduler struct {
}

func (RejectScheduler) GetFullName() string {
	return RejectSchedulerSchedulerName
}

func (s RejectScheduler) GetScheduler() *types.SchedulerDescriptor {
	return &types.SchedulerDescriptor{
		Name:       RejectSchedulerSchedulerName,
		Parameters: []string{},
	}
}

func (s RejectScheduler) Schedule(req *types.ServiceRequest) (*JobResult, error) {
	log.Log.Debugf("Scheduling job %s", req.ServiceName)
	now := time.Now()
	timingsStart := types.TimingsStart{ArrivedAt: &now}

	// always deliberately reject the job
	result := JobResult{TimingsStart: &timingsStart, Scheduler: s.GetFullName()}
	return &result, JobDeliberatelyRejected{}
}
