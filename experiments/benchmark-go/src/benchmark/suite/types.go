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

package suite

const (
	RES_HEADER_EXTERNALLY_EXECUTED = "X-P2pfaas-Externally-Executed"
	RES_HEADER_HOPS                = "X-P2pfaas-Hops"

	RES_HEADER_EXECUTION_TIME  = "X-P2pfaas-Timing-Execution-Time-Seconds"
	RES_HEADER_TOTAL_TIME      = "X-P2pfaas-Timing-Total-Time-Seconds"
	RES_HEADER_SCHEDULING_TIME = "X-P2pfaas-Timing-Scheduling-Time-Seconds"
	RES_HEADER_PROBING_TIME    = "X-P2pfaas-Timing-Probing-Time-Seconds"
	RES_HEADER_PEERS_LIST_IP   = "X-P2pfaas-Peers-List-Ip"

	RES_HEADER_SCHEDULING_TIME_LIST = "X-P2pfaas-Timing-Scheduling-Seconds-List"
	RES_HEADER_TOTAL_TIME_LIST      = "X-P2pfaas-Timing-Total-Seconds-List"
	RES_HEADER_PROBING_TIME_LIST    = "X-P2pfaas-Timing-Probing-Seconds-List"

	RES_HEADER_SCHEDULER_LEARNING_EID    = "X-P2pfaas-Scheduler-Learning-Eid"
	RES_HEADER_SCHEDULER_LEARNING_STATE  = "X-P2pfaas-Scheduler-Learning-State"
	RES_HEADER_SCHEDULER_LEARNING_ACTION = "X-P2pfaas-Scheduler-Learning-Action"
	RES_HEADER_SCHEDULER_LEARNING_EPS    = "X-P2pfaas-Scheduler-Learning-Eps"
)
