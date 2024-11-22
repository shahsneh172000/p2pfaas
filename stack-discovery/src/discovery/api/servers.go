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

package api

import (
	"discovery/config"
	"discovery/db"
	"discovery/errors"
	"discovery/log"
	"discovery/types"
	"discovery/utils"
	"encoding/json"
	"io"
	"net"
	"net/http"
)

func ServersGetList(w http.ResponseWriter, r *http.Request) {
	// add the requestor's ip if it is a machine
	if r.Header.Get("User-Agent") == utils.UserAgentMachine {
		clientIp := net.ParseIP(utils.IsolateIPFromPort(r.Header.Get(config.GetParamIp)))
		if len(clientIp) > 0 {
			log.Log.Debug("Machine %s requested list, adding/updating my list", clientIp)
			err := db.MachineAdd(&types.Machine{
				IP:        r.Header.Get(config.GetParamIp),
				Name:      r.Header.Get(config.GetParamName),
				GroupName: r.Header.Get(config.GetParamGroupName),
				Alive:     true,
				DeadPolls: 0,
			}, true)
			if err != nil {
				log.Log.Debugf("Cannot add machine %s: %s", r.Header.Get(config.GetParamIp), err.Error())
			}
		} else {
			log.Log.Debugf("Requestor %s is a machine but its IP is not valid", r.RemoteAddr)
		}
	} else {
		log.Log.Debugf("Success, User-Agent: \"%s\"", r.Header.Get("User-Agent"))
	}

	// prepare the output
	aliveMachines, err := db.MachinesGetAlive()
	// if empty reply with []
	if aliveMachines == nil {
		aliveMachines = []types.Machine{}
	}

	out, err := json.Marshal(aliveMachines)
	if err != nil {
		log.Log.Debugf("Cannot marshal json")
		errors.ReplyWithError(w, errors.GenericError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	// set machine meta
	w.Header().Set(config.GetParamIp, config.GetMachineIp())
	w.Header().Set(config.GetParamName, config.GetMachineId())
	w.Header().Set(config.GetParamGroupName, config.GetMachineGroupName())

	_, _ = io.WriteString(w, string(out))
}

func ServersReset(w http.ResponseWriter, r *http.Request) {
	err := db.MachineRemoveAll()
	if err != nil {
		log.Log.Errorf("Cannot delete all machines: %s", err)
		w.WriteHeader(500)
		return
	}

	w.WriteHeader(200)
}
