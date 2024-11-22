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

package db

import (
	"benchmark/log"
	"benchmark/types"
	"bufio"
	"database/sql"
	"fmt"
	_ "github.com/mattn/go-sqlite3"
	"github.com/schollz/sqlite3dump"
	"os"
	"strconv"
	"strings"
	"sync"
	"time"
)

var db *sql.DB
var dbMutex sync.Mutex

func Init() {
	var err error

	db, err = sql.Open("sqlite3", ":memory:")
	// db, err = sql.Open("sqlite3", dbPath)
	if err != nil {
		log.Log.Fatalf("Cannot create database: %s", err)
	}
	if db == nil {
		log.Log.Fatalf("DB is nil")
	}

	// having multiple connections is not feasible in sqlite
	db.SetMaxOpenConns(1)

	err = createTables(db)
	if err != nil {
		log.Log.Fatalf("Cannot create tables: %s", err)
	}
}

func Close() {
	err := db.Close()
	if err != nil {
		log.Log.Errorf("Cannot close db: %s", err)
	}
}

func createTables(dbToUse *sql.DB) error {
	// create table if not exists
	sqlTableJobs := `
        CREATE TABLE jobs (
						 node_id integer, 
						 req_id integer, 
						 type_id integer,
						 payload_name text, 
						 requests_rate real,
						 time_total real, 
						 time_execution real, 
						 times_parsed integer, 
						 res_status_code integer,
						 res_error_code integer,
						 req_net_error integer,
						 req_net_error_message string,
						 externally_executed integer,
						 timestamp_start real,
						 timestamp_end real,
						 learning_state string,
						 learning_action real,
						 learning_eps real,
						 learning_reward real
					 )`

	sqlTableTimings := `
		CREATE TABLE timings (
						 node_id integer, 
						 req_id integer, 
						 payload_name text,
						 requests_rate real,
						 index_i integer,
						 time_type text, 
						 time_value real
					 )`

	sqlTableValues := `
		CREATE TABLE values_strings (
						 node_id integer, 
						 req_id integer, 
						 payload_name text,
						 requests_rate real,
						 index_i integer,
						 value_type text, 
						 value_value text
					 )`

	tx, err := dbToUse.Begin()
	if err != nil {
		log.Log.Errorf("Could create transaction: %s", err)
		return err
	}

	_, err = tx.Exec(sqlTableJobs)
	if err != nil {
		log.Log.Errorf("Cannot create table: %s", err)
		return err
	}

	_, err = tx.Exec(sqlTableTimings)
	if err != nil {
		log.Log.Errorf("Cannot create table: %s", err)
		return err
	}

	_, err = tx.Exec(sqlTableValues)
	if err != nil {
		log.Log.Errorf("Cannot create table: %s", err)
		return err
	}

	err = tx.Commit()
	if err != nil {
		log.Log.Errorf("Could not commit for create tables: %s", err)
		return err
	}

	return nil
}

/*
 * Disk save
 */

func SaveDBToDisk(filename string) {
	log.Log.Debugf("Acquiring lock")
	dbMutex.Lock()
	log.Log.Debugf("Acquired lock")

	var err error

	log.Log.Infof("Starting dump db to sql script")

	startTime := time.Now()

	fileSqlPath := fmt.Sprintf("%s.sql", filename)
	fileSql, err := os.Create(fileSqlPath)
	if err != nil {
		log.Log.Errorf("Cannot open file for db: %s", err)
		dbMutex.Unlock()
		return
	}

	// var b bytes.Buffer
	// out := bufio.NewWriter(&b)

	options1 := sqlite3dump.WithTransaction(true)
	options2 := sqlite3dump.WithDropIfExists(false)
	options3 := sqlite3dump.WithMigration()

	// dump the db to .sql file
	err = sqlite3dump.DumpDB(db, fileSql, options1, options2, options3)
	if err != nil {
		log.Log.Errorf("Cannot save db: %s", err)
		dbMutex.Unlock()
		return
	}

	// _, err = file.Write(b.Bytes())
	// if err != nil {
	//	log.Log.Errorf("Cannot write db to file: %s", err)
	//	dbMutex.Unlock()
	//	return
	// }

	err = fileSql.Close()
	if err != nil {
		log.Log.Errorf("Cannot close db file: %s", err)
		dbMutex.Unlock()
		return
	}

	endTime := time.Now()

	log.Log.Infof("Copied db to sql script file in %fs", float64(endTime.Sub(startTime).Microseconds())/1000000.0)

	dbMutex.Unlock()

	log.Log.Infof("Starting dump db to sql binary file")

	startTime = time.Now()

	fileSql, err = os.Open(fmt.Sprintf("%s.sql", filename))
	if err != nil {
		log.Log.Errorf("Cannot open file for db: %s", err)
		return
	}

	// db, err = sql.Open("sqlite3", ":memory:")
	db, err = sql.Open("sqlite3", fmt.Sprintf("%s.db", filename))
	if err != nil {
		log.Log.Fatalf("Cannot create database: %s", err)
		return
	}
	if db == nil {
		log.Log.Fatalf("DB is nil")
		return
	}

	// create tables
	err = createTables(db)
	if err != nil {
		log.Log.Fatalf("Cannot create tables: %s", err)
		return
	}

	// add values
	fileScanner := bufio.NewScanner(fileSql)
	fileScanner.Split(bufio.ScanLines)

	var line string
	for fileScanner.Scan() {
		line = fileScanner.Text()
		// log.Log.Infof("Executing line: %s", line)

		_, err = db.Exec(line)
		if err != nil {
			log.Log.Errorf("Cannot exec line %s: %s", line, err)
			return
		}
	}

	// close db
	err = db.Close()
	if err != nil {
		log.Log.Errorf("Cannot close db file: %s", err)
	}

	// close file
	err = fileSql.Close()
	if err != nil {
		log.Log.Errorf("Cannot close db file: %s", err)
	}

	// remove sql file
	if err = os.Remove(fileSqlPath); err != nil {
		log.Log.Errorf("Cannot remove file: %s", fileSqlPath)
	}

	endTime = time.Now()

	log.Log.Infof("Copied db to file in %fs", float64(endTime.Sub(startTime).Microseconds())/1000000.0)
}

/*
 * Exported
 */

func LogJobEnd(result *types.BenchmarkResult) error {
	dbMutex.Lock()

	timeParsed := 0
	if result.TimesParsed {
		timeParsed = 1
	}

	externallyExecuted := 0
	if result.ExternallyExecuted {
		externallyExecuted = 1
	}

	// better display learning state
	learningStateToUse := ""
	learningStateComponents := strings.Split(result.LearningState, ",")
	if len(learningStateComponents) > 0 {
		for i, state := range learningStateComponents {
			stateInt, _ := strconv.ParseFloat(state, 64)

			learningStateToUse = fmt.Sprintf("%s%d", learningStateToUse, int64(stateInt))

			if i < len(learningStateComponents)-1 {
				learningStateToUse = fmt.Sprintf("%s,", learningStateToUse)
			}
		}
	}

	tx, err := db.Begin()
	if err != nil {
		log.Log.Errorf("Could not create transaction: %s", err)
		return err
	}

	_, err = tx.Exec("INSERT INTO jobs VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
		result.NodeId,
		result.ReqId,
		result.TypeId,
		result.PayloadName,
		result.RequestsRate,
		result.TimeTotal,
		result.TimeExecution,
		timeParsed,
		result.ResponseStatusCode,
		result.ResponseErrorCode,
		result.RequestNetError,
		result.RequestNetErrorMessage,
		externallyExecuted,
		float64(result.TimestampStart.UnixMicro())/float64(1000*1000),
		float64(result.TimestampEnd.UnixMicro())/float64(1000*1000),
		learningStateToUse,
		result.LearningAction,
		result.LearningEpsilon,
		result.LearningReward,
	)
	if err != nil {
		dbMutex.Unlock()
		return err
	}

	for i, value := range result.TimesProbing {
		logJobTiming(tx, result.NodeId, result.ReqId, result.PayloadName, result.RequestsRate, i, TIME_TYPE_PROBING, value)
	}
	for i, value := range result.TimesService {
		logJobTiming(tx, result.NodeId, result.ReqId, result.PayloadName, result.RequestsRate, i, TIME_TYPE_SERVICE, value)
	}
	for i, value := range result.TimesScheduling {
		logJobTiming(tx, result.NodeId, result.ReqId, result.PayloadName, result.RequestsRate, i, TIME_TYPE_SCHEDULING, value)
	}
	for i, value := range result.PeersListIp {
		logJobValue(tx, result.NodeId, result.ReqId, result.PayloadName, result.RequestsRate, i, VALUE_TYPE_PEER_IP, value)
	}

	err = tx.Commit()
	if err != nil {
		log.Log.Errorf("Could not do the commit: %s", err)
		dbMutex.Unlock()
		return err
	}

	dbMutex.Unlock()

	return nil
}

func logJobTiming(tx *sql.Tx, nodeId string, reqId int64, payloadName string, requestsRate float64, index int, timeType string, timeValue float64) {
	_, err := tx.Exec(`INSERT INTO timings VALUES (?,?,?,?,?,?,?)`,
		nodeId, reqId, payloadName, requestsRate, index, timeType, timeValue)
	if err != nil {
		log.Log.Errorf("Cannot log time nodeId=%s reqId=%s err=%s", nodeId, reqId, err)
	}
}

func logJobValue(tx *sql.Tx, nodeId string, reqId int64, payloadName string, requestsRate float64, index int, valueType string, value string) {
	_, err := tx.Exec(`INSERT INTO values_strings VALUES (?,?,?,?,?,?,?)`,
		nodeId, reqId, payloadName, requestsRate, index, valueType, value)
	if err != nil {
		log.Log.Errorf("Cannot log time nodeId=%s reqId=%s err=%s", nodeId, reqId, err)
	}
}
