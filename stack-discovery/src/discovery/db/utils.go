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

package db

import (
	"context"
	"discovery/config"
	"discovery/log"
	"discovery/types"
	"fmt"
	"time"
)

// DeclarePollFailed declares the machine as dead when the threshold of dead polls is reached
func DeclarePollFailed(machine *types.Machine) {
	machine.DeadPolls++

	// if machine already marked as not alive then delete from DB
	if !machine.Alive {
		log.Log.Warningf("Deleting machine %s since already dead", machine.IP)
		return
	}

	// otherwise declar as not alive
	if machine.DeadPolls >= config.GetMachineDeadPollsRemovingThreshold() {
		machine.Alive = false
	}
	machine.LastUpdate = time.Now().Unix()

	_, err := MachineUpdate(machine)
	if err != nil {
		log.Log.Warningf("Could not update the machine %s", machine.IP)
	}
	log.Log.Debugf("Poll for machine %s failed", machine.IP)
}

// DeclarePollSucceeded declare the machine as alive and reset the dead polls counter
func DeclarePollSucceeded(machine *types.Machine, ping float64) {
	machine.Ping = ping
	machine.Alive = true
	machine.DeadPolls = 0
	machine.LastUpdate = time.Now().Unix()

	_, err := MachineUpdate(machine)
	if err != nil {
		log.Log.Warningf("Could not update the machine %s", machine.IP)
	}
	log.Log.Debugf("Poll for machine %s succeeded", machine.IP)
}

/*
 * Core
 */

func getDatabaseDirPath() string {
	return config.GetDataPath() // + "/" + DatabasePath
}

func getDatabaseFilePath() string {
	return getDatabaseDirPath() + "/" + DatabaseName
}

func executeTransaction(query string, args ...interface{}) error {
	tx, err := db.Begin()
	if err != nil {
		return fmt.Errorf("cannot begin transaction: %s", err.Error())
	}

	stmt, err := db.Prepare(query)
	if err != nil {
		return fmt.Errorf("cannot prepare query: %s", err.Error())
	}

	_, err = stmt.ExecContext(context.Background(), query, args)
	if err != nil {
		return fmt.Errorf("cannot execute query: %s", err.Error())
	}

	err = tx.Commit()
	if err != nil {
		return fmt.Errorf("cannot commit query: %s", err.Error())
	}

	return nil
}
