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

import "fmt"

type JobCannotBeScheduled struct {
	reason string
}

func (e JobCannotBeScheduled) Error() string {
	return fmt.Sprintf("Job cannot be scheduled: %s", e.reason)
}

type JobCannotBeForwarded struct {
	neighborHost string
	reason       string
}

func (e JobCannotBeForwarded) Error() string {
	return fmt.Sprintf("Job cannot be forwarded to neighbor %s: %s", e.neighborHost, e.reason)
}

type PeerResponseNil struct {
	neighborHost string
}

func (e PeerResponseNil) Error() string {
	return fmt.Sprintf("Peer %s response is nil", e.neighborHost)
}

type JobDeliberatelyRejected struct {
}

func (e JobDeliberatelyRejected) Error() string {
	return fmt.Sprintf("Job has been deliberately rejected")
}

type CannotChangeScheduler struct{}

func (e CannotChangeScheduler) Error() string {
	return "SchedulerDescriptor cannot be changed right now"
}

type CannotRetrieveAction struct {
	err error
}

func (e CannotRetrieveAction) Error() string {
	return fmt.Sprintf("The action to be taken cannot be retrieved: %s", e.err)
}

type CannotRetrieveRecipientNode struct {
	err error
}

func (e CannotRetrieveRecipientNode) Error() string {
	return fmt.Sprintf("The recipient node cannot be retrieved: %s", e.err)
}

type BadSchedulerParameters struct{}

func (e BadSchedulerParameters) Error() string {
	return "Bad passed parameters for scheduler"
}
