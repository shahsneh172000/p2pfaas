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

type ServiceRequest struct {
	Id                 uint64 // unique id assigned to the request
	IdTracing          string
	ServiceName        string // Name of the function to be executed
	ServiceType        int64  // type of the task to be executed
	Payload            []byte
	PayloadContentType string
	Headers            *map[string]string
	External           bool // If the service request comes from another node and not user
	ExternalJobRequest *PeerJobRequest
}
