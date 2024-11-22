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

package service_learning

import (
	"fmt"
	"github.com/gorilla/websocket"
	"scheduler/config"
	"scheduler/log"
	"scheduler/utils"
	"strconv"
	"strings"
	"sync"
	"time"
)

type SocketActRequest struct {
	entryAct  *EntryAct
	doneMutex *sync.WaitGroup

	outputAction *EntryActOutput
	outputError  error
}

const SocketPoolSize = 20

var socketPool []*websocket.Conn
var socketPoolBusy []bool
var socketPoolMutex = sync.Mutex{}

var socketServerInit = false

var socketPendingRequestsList []*SocketActRequest
var socketPendingRequestsListMutex = sync.Mutex{}

var socketConsumersSemaphore = make(utils.Semaphore, SocketPoolSize)

var socketFreeSlotsSemaphore = make(utils.Semaphore, SocketPoolSize*3) // queue len for act requests
var socketBusySlotsSemaphore = make(utils.Semaphore, 0)

func Start() {
	var err error
	var conn *websocket.Conn

	log.Log.Debugf("Starting learner service socket pool")

	// reset everything
	socketPool = []*websocket.Conn{}
	socketPoolBusy = []bool{}
	socketPoolMutex = sync.Mutex{}

	socketPendingRequestsList = []*SocketActRequest{}
	socketPendingRequestsListMutex = sync.Mutex{}

	socketConsumersSemaphore = make(utils.Semaphore, SocketPoolSize)
	socketFreeSlotsSemaphore = make(utils.Semaphore, SocketPoolSize*3) // queue len for act requests
	socketBusySlotsSemaphore = make(utils.Semaphore, 0)

	// try to connect
	for i := 0; i < SocketPoolSize; i++ {
		for {
			conn, err = socketConnect()
			if err != nil {
				log.Log.Errorf("Cannot connect to learner socket #%d, retrying in 5 seconds: err=%s", i, err)
				time.Sleep(5 * time.Second)
				continue
			}

			log.Log.Infof("Initialized socket #%d: addr=%s==>%s", i+1, conn.LocalAddr().String(), conn.RemoteAddr().String())
			break
		}

		socketPool = append(socketPool, conn)
		socketPoolBusy = append(socketPoolBusy, false)
	}

	log.Log.Infof("Successfully prepared socket pool for learning service")

	socketServerInit = true

	go socketLooper()
}

func Stop() {
	if !socketServerInit {
		return
	}

	var err error

	log.Log.Debugf("Closing socket pool gracefully: len(socketPool)=%d", len(socketPool))

	for i, sock := range socketPool {
		err = sock.Close()
		if err != nil {
			log.Log.Warningf("Cannot close socket #%d: err=%s", i, err)
		}
	}

	socketServerInit = false

	// trigger busy for stopping the looper
	socketBusySlotsSemaphore.Signal()
}

// SocketAct executes the act by using the websocket to learner service
func SocketAct(act *EntryAct) (*EntryActOutput, error) {
	req := SocketActRequest{
		entryAct:  act,
		doneMutex: &sync.WaitGroup{},

		outputAction: &EntryActOutput{},
	}
	req.doneMutex.Add(1)

	// wait for free slots
	socketFreeSlotsSemaphore.Wait(1)

	// enqueue
	socketPendingRequestsListMutex.Lock()
	socketPendingRequestsList = append(socketPendingRequestsList, &req)
	socketPendingRequestsListMutex.Unlock()

	// signal busy slots
	socketBusySlotsSemaphore.Signal()

	// wait for the result
	req.doneMutex.Wait()

	// return to client
	return req.outputAction, nil
}

/*
 * Internals
 */

func socketConnect() (*websocket.Conn, error) {
	var err error
	var socket *websocket.Conn

	socketUrl := fmt.Sprintf("ws://%s:8765", config.GetServiceLearningListeningHost()) //  + "/socket"

	log.Log.Debugf("Trying to connect to websocket to: %s", socketUrl)

	socket, _, err = websocket.DefaultDialer.Dial(socketUrl, nil)
	if err != nil {
		log.Log.Errorf("Error connecting to websocket server:", err)
		return nil, err
	}

	return socket, nil
}

func socketLooper() {
	log.Log.Infof("Started looper for learning requests")

	for {
		log.Log.Debugf("Waiting for free socket")
		// wait for free space
		socketConsumersSemaphore.Wait(1)

		log.Log.Debugf("Waiting for request to process")
		// wait for request
		socketBusySlotsSemaphore.Wait(1)

		if !socketServerInit {
			log.Log.Infof("Exiting from socketLooper")
			break
		}

		log.Log.Debugf("Processing request")
		// dequeue and process
		socketPendingRequestsListMutex.Lock()

		requestToProcess := socketPendingRequestsList[0]
		socketPendingRequestsList = socketPendingRequestsList[1:]
		go socketProcessRequest(requestToProcess)

		socketPendingRequestsListMutex.Unlock()

		// signal free slot
		socketFreeSlotsSemaphore.Signal()
	}
}

func socketProcessRequest(req *SocketActRequest) {
	var err error
	var msg []byte

	// find free socket
	bookedSlotIndex := socketPoolSlotBook()

	log.Log.Debugf("Processing request: bookedSlotIndex=%d req=%s", bookedSlotIndex, *req)

	// send and receive from that socket
	connection := socketPool[bookedSlotIndex]

	// free
	defer func() {
		log.Log.Debugf("Releasing resources for bookedSlotIndex=%d", bookedSlotIndex)

		socketPoolSlotRelease(bookedSlotIndex)
		socketConsumersSemaphore.Signal()
		req.doneMutex.Done()
	}()

	firstTime := true

	for {
		// retry to recreate the socket if not first time
		if !firstTime {
			log.Log.Infof("Socket #%d recreating...", bookedSlotIndex)

			_ = connection.Close()

			// if error retry to set up the socket
			socketPool[bookedSlotIndex], err = socketConnect()
			if err != nil {
				log.Log.Errorf("Cannot re-create the socket, giving up: %s", err)
				req.outputError = err
				return
			}

			connection = socketPool[bookedSlotIndex]
			log.Log.Infof("Socket #%d recreated successfully", bookedSlotIndex)
		}

		// write message
		// messageBytes, err := json.Marshal(req.state)
		err = connection.WriteJSON(req.entryAct.State)
		if err != nil {
			req.outputError = err
			log.Log.Errorf("Cannot write message to socket (firstTime=%v): %s", firstTime, err)

			if !firstTime {
				return
			}

			firstTime = false
			continue
		}

		// receive message
		_, msg, err = connection.ReadMessage()
		if err != nil {
			req.outputError = err
			log.Log.Errorf("Cannot parse read reply message (firstTime=%v): %s", firstTime, err)

			if !firstTime {
				return
			}

			firstTime = false
			continue
		}

		// err = json.Unmarshal(msg, &req.outputAction)
		msgComponents := strings.Split(string(msg), ",")
		req.outputAction.Action, err = strconv.ParseFloat(msgComponents[0], 64)
		req.outputAction.Eps, err = strconv.ParseFloat(msgComponents[1], 64)
		if err != nil {
			req.outputError = err
			log.Log.Errorf("Cannot parse float from reply message (firstTime=%v): %s", firstTime, err)

			if !firstTime {
				return
			}

			firstTime = false
			continue
		}

		break
	}

}

func socketPoolSlotBook() int64 {
	socketPoolMutex.Lock()
	i := 0
	for {
		if !socketPoolBusy[i] {
			socketPoolBusy[i] = true
			socketPoolMutex.Unlock()
			return int64(i)
		}

		i = (i + 1) % SocketPoolSize
	}
}

func socketPoolSlotRelease(index int64) {
	socketPoolMutex.Lock()
	socketPoolBusy[index] = false
	socketPoolMutex.Unlock()
}
