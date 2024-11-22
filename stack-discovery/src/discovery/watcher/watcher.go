/*
 * P2PFaaS - A framework for FaaS Load Balancing
 * Copyright (c) 2019. Gabriele Proietti Mattia <pm.gabriele@outlook.com>
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

// Package watcher implements the poller thread to update the list of known nodes
package watcher

import (
	"discovery/config"
	"discovery/db"
	"discovery/log"
	"discovery/types"
	"encoding/json"
	"time"
)

// var httpTransport *http.Transport

func init() {
	/*
		httpTransport = &http.Transport{
			MaxIdleConns:        24,
			IdleConnTimeout:     64,
			MaxIdleConnsPerHost: 8,
			DisableKeepAlives:   false,
			DialContext: (&net.Dialer{
				KeepAlive: 120 * time.Second,
			}).DialContext,
		}
	*/
}

func PollingLooper() {
	for {
		// check if we have basic configuration parameters
		if config.GetMachineIp() == "" {
			log.Log.Warningf("Machine has not configured its IP, service is idle. Retrying in 30 seconds...")
			time.Sleep(30 * time.Second)
			continue
		}

		machinesToPoll, err := db.MachinesGetAliveAndSuspected()
		if err != nil {
			log.Log.Debugf("Cannot get machines to poll, retrying in 30 seconds")
			time.Sleep(30 * time.Second)
			continue
		}

		log.Log.Debugf("Starting poll for %d machines", len(machinesToPoll))
		for _, m := range machinesToPoll {
			log.Log.Debugf("Polling machine %s", m.IP)

			// check if machine is actually the current node
			if m.IP == config.GetMachineIp() {
				// remove the entry from the db
				log.Log.Infof("Removing current machine '%s' from entry list", m.IP)
				err = db.MachineRemove(m.IP)
				if err != nil {
					log.Log.Errorf("Cannot remove self machine entry in list: %s", err)
				}
				continue
			}

			// poll machine
			ping, err := pollMachine(&m)

			// check if poll succeed or not
			if err != nil {
				db.DeclarePollFailed(&m)
			} else {
				db.DeclarePollSucceeded(&m, ping.Seconds())
			}
		}

		time.Sleep(time.Duration(config.GetPollTime()) * time.Second)
	}
}

// PollMachine checks if a machine is alive but the polled machine returns all the alive machine IPs that it knows
func pollMachine(machine *types.Machine) (*time.Duration, error) {
	// make the get
	startTime := time.Now()
	res, err := GetForPoll(machine.IP)
	elapsedTime := time.Since(startTime)
	if err != nil {
		log.Log.Debugf("Error while polling machine %s: %s", machine.IP, err.Error())
		return nil, err
	}

	// check the answering machine's ip, if it is different from our it means that the machine changed
	// its ip, so update it
	if res.Header.Get(config.GetParamIp) != machine.IP {
		answeringMachine, err := db.MachineGet(machine.IP)
		if err == nil && answeringMachine != nil {
			answeringMachine.IP = res.Header.Get(config.GetParamIp)
			answeringMachine.Name = res.Header.Get(config.GetParamName)
			answeringMachine.GroupName = res.Header.Get(config.GetParamGroupName)
			_, _ = db.MachineUpdate(answeringMachine)
		}
	}

	// update parameters, they may change over time
	machine.Name = res.Header.Get(config.GetParamName)
	machine.GroupName = res.Header.Get(config.GetParamGroupName)

	// decode machine list
	var machines []types.Machine
	err = json.NewDecoder(res.Body).Decode(&machines)
	_ = res.Body.Close()
	if err != nil {
		log.Log.Debugf("Error while parsing polled machine %s response: %s", machine.IP, err.Error())
		return nil, err
	}
	// add machines list to db
	for _, m := range machines {
		err = db.MachineAdd(&m, true)
	}

	return &elapsedTime, nil
}
