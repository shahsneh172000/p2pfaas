/*
 * P2PFaaS - A framework for FaaS Load Balancing
 * Copyright (c) 2020. Gabriele Proietti Mattia <pm.gabriele@outlook.com>
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
 *
 */

package db

import (
	"database/sql"
	"discovery/config"
	"discovery/log"
	"discovery/types"
	_ "github.com/mattn/go-sqlite3"
	"os"
	"strings"
	"time"
)

var db *sql.DB

type Error struct {
	Reason string
}

func (e Error) Error() string {
	return e.Reason
}

func initBackend() {
	log.Log.Debugf("Initializing DB sqlite3 backend")

	var err error

	// create directory if does not exists
	err = os.MkdirAll(getDatabaseDirPath(), 0755)
	if err != nil {
		log.Log.Fatalf("Cannot create db directory: %s", err.Error())
		return
	}

	// init db
	db, err = sql.Open("sqlite3", getDatabaseFilePath())
	if err != nil {
		log.Log.Fatal("Cannot init sqlite database: %s", err.Error())
		return
	}
	log.Log.Debugf("Created DB at %s: %s", getDatabaseFilePath(), db)

	err = initDb()
	if err != nil {
		log.Log.Fatal("Cannot init sqlite tables: %s", err.Error())
		return
	}

	log.Log.Info("Sqlite DB init successfully")
}

func initDb() error {
	var err error
	_, err = db.Exec(`create table if not exists machines (
								id integer primary key, 
								ip text unique, 
								name text, 
								group_name text, 
								ping real, 
								last_update integer, 
								alive integer, 
								dead_polls integer
                            )`)
	if err != nil {
		log.Log.Errorf("Cannot init machines: %s", types.MachinesCollectionName)
		return err
	}
	return nil
}

// MachineAdd tries to add the machine to database, if already present if declareAlive is true then the machine will be
// redeclared as alive/home/gabrielepmattia/Coding/p2p-faas/stack-discovery
func MachineAdd(machine *types.Machine, declareAlive bool) error {
	// skip if we try to add the current machine
	if machine.IP == config.GetMachineIp() {
		return Error{Reason: "Could not add yourself as machine"}
	}
	// skip docker IPs
	if strings.Index(machine.IP, "172.17") == 0 {
		return Error{Reason: "Ignoring IPs that starts with docker subnet: 172.17.0.0/16"}
	}

	// check if machine already exists
	machineRetrieved, err := MachineGet(machine.IP)
	if machineRetrieved != nil && declareAlive {
		log.Log.Debugf("Machine %s already exists", machine.IP)
		// if yes, set machine to alive and update
		machine.Alive = true
		machine.DeadPolls = 0
		machine.LastUpdate = time.Now().Unix()

		_, err = MachineUpdate(machine)
		if err != nil {
			log.Log.Errorf("Cannot update the machine row: %s", err.Error())
			return err
		}
		return nil
	} else {
		log.Log.Debugf("Machine %s does not exist", machine.IP)
	}

	// add the machine
	tx, err := db.Begin()
	if err != nil {
		log.Log.Errorf("Cannot begin transaction: %s", err.Error())
		return err
	}
	stmt, err := db.Prepare("insert into machines (ip, name, group_name, ping, last_update, alive, dead_polls) values (?,?,?,?,?,?,?)")
	if err != nil {
		log.Log.Errorf("Cannot prepare query: %s", err.Error())
		return err
	}
	_, err = stmt.Exec(machine.IP, machine.Name, machine.GroupName, machine.Ping, time.Now().Unix(), machine.Alive, machine.DeadPolls)
	if err != nil {
		log.Log.Errorf("Cannot execute query: %s", err.Error())
		return err
	}
	err = tx.Commit()
	if err != nil {
		log.Log.Errorf("Cannot commit query: %s", err.Error())
		return err
	}

	return nil
}

func MachinesGet() ([]types.Machine, error) {
	rows, err := db.Query("select * from machines order by name")
	if err != nil {
		log.Log.Errorf("Cannot retrieve machines: %s", err.Error())
		return nil, err
	}
	return machinesParseRows(rows)
}

// MachinesGetAlive retrieves machines that surely are alive
func MachinesGetAlive() ([]types.Machine, error) {
	rows, err := db.Query("select * from machines where alive = 1 order by name")
	if err != nil {
		log.Log.Errorf("Cannot retrieve machines: %s", err.Error())
		return nil, err
	}
	return machinesParseRows(rows)
}

func MachinesGetAliveAndSuspected() ([]types.Machine, error) {
	rows, err := db.Query("select * from machines where alive = 1 and dead_polls >= 0 and dead_polls < ?  order by name", config.GetMachineDeadPollsRemovingThreshold())
	if err != nil {
		log.Log.Errorf("Cannot retrieve machines: %s", err.Error())
		return nil, err
	}
	return machinesParseRows(rows)
}

func MachineGet(ip string) (*types.Machine, error) {
	log.Log.Debugf("Searching machine %s", ip)
	rows, err := db.Query("select * from machines where ip = ?", ip)
	if err != nil {
		log.Log.Errorf("Cannot retrieve machines: %s", err.Error())
		return nil, err
	}
	machines, err := machinesParseRows(rows)
	if err != nil {
		return nil, err
	}
	if len(machines) > 0 {
		return &machines[0], nil
	}
	return nil, nil
}

func MachineUpdate(machine *types.Machine) (int64, error) {
	res, err := db.Exec(`
				update machines set 
                    name = ?, 
                    group_name = ?, 
                    ping = ?, 
                    last_update = ?, 
                    alive = ?, 
                    dead_polls = ? 
				where 
				      ip = ?`,
		machine.Name,
		machine.GroupName,
		machine.Ping,
		machine.LastUpdate,
		machine.Alive,
		machine.DeadPolls,
		machine.IP,
	)
	if err != nil {
		log.Log.Errorf("Cannot update machine %s: %s", machine.IP, err.Error())
		return 0, err
	}
	rowsAff, _ := res.RowsAffected()
	return rowsAff, nil
}

func MachineRemove(ip string) error {
	_, err := db.Exec("delete from machines where ip = ?", ip)
	if err != nil {
		log.Log.Errorf("Cannot remove machine %s: %s", ip, err.Error())
		return err
	}
	return nil
}

func MachineRemoveAll() error {
	res, err := db.Exec("delete from machines")
	if err != nil {
		log.Log.Errorf("Cannot remote machines: %s", err.Error())
		return err
	}
	deletedRows, _ := res.RowsAffected()
	log.Log.Debugf("Deleted: %d rows", deletedRows)
	return nil
}

func machinesParseRows(rows *sql.Rows) ([]types.Machine, error) {
	var machines []types.Machine
	var err error
	totalRows := 0

	for rows.Next() {
		totalRows += 1
		var tempMachine types.Machine
		err = rows.Scan(&tempMachine.ID, &tempMachine.IP, &tempMachine.Name, &tempMachine.GroupName, &tempMachine.Ping, &tempMachine.LastUpdate, &tempMachine.Alive, &tempMachine.DeadPolls)
		if err != nil {
			log.Log.Errorf("Cannot scan row: %s", err.Error())
			continue
		}
		machines = append(machines, tempMachine)
	}
	log.Log.Debugf("Total rows: %d", totalRows)
	return machines, nil
}
