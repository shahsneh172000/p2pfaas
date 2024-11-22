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
	"scheduler/types"
)

// JobResult represents the result of the execution of a task
type JobResult struct {
	Response              *types.APIResponse     `json:"response"`
	ProbingMessages       uint                   `json:"probing_messages"`
	ExternalExecution     bool                   `json:"external_execution"`
	ExternalExecutionInfo *ExternalExecutionInfo `json:"external_executed_info"`
	ErrorExecution        bool                   `json:"error_execution"`
	TimingsStart          *types.TimingsStart    `json:"timings_start"`
	Timings               *types.Timings         `json:"timings"`
	ResponseHeaders       *map[string]string     `json:"response_headers"` // custom headers to be returned to clients
	Scheduler             string                 `json:"scheduler"`        // the scheduler that executed the job
}

// ExternalExecutionInfo holds information about the external execution of the task
type ExternalExecutionInfo struct {
	PeersList []types.PeersListMember `json:"peers_list"`
}
