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

import (
	"benchmark/db"
	"benchmark/learning"
	"benchmark/log"
	"benchmark/traffic"
	"benchmark/types"
	"benchmark/utils"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"math/rand"
	"net/http"
	"os"
	"strconv"
	"sync"
	"time"
)

func _StartBenchmarkLambdaArrayMultiPayload(lambdas []float64, params *types.BenchmarkBasicParams) {
	// preliminary checks
	if lambdas == nil {
		log.Log.Errorf("lambdas is nil")
		return
	}

	if params.Hosts == nil || len(params.Hosts) == 0 {
		log.Log.Errorf("hosts is nil or 0")
		return
	}

	var payloads []*types.Payload

	// loop over all payloads
	for _, payloadName := range params.Payloads {
		log.Log.Infof("Benchmarking payload %s", payloadName)

		var wgEnd sync.WaitGroup
		var wgStart sync.WaitGroup

		payload, err := PreparePayload(params.DirPayloads, payloadName, 0)
		if err != nil {
			log.Log.Errorf("Cannot parse payload")
		}
		payloads = []*types.Payload{payload}

		wgStart.Add(1)
		startTime := time.Now()

		// start bench to every host at given lambda with that payload
		for nodeId, host := range params.Hosts {
			log.Log.Infof("Benchmarking machine %s", host)

			wgEnd.Add(1)
			go StartBenchmarkSingleMachine(&wgEnd, &wgStart, &startTime, int64(nodeId), host, nil, &payloads, params)
		}

		// start all threads at the same time
		wgStart.Done()

		// wait for all threads to stop
		wgEnd.Wait()
	}
}

func StartBenchmarkMixPayloads(trafficModel traffic.Model, params *types.BenchmarkBasicParams) {
	// preliminary checks
	if trafficModel == nil {
		log.Log.Errorf("trafficModel is nil")
		return
	}

	if params.Hosts == nil || len(params.Hosts) == 0 {
		log.Log.Errorf("hosts is nil or 0")
		return
	}

	log.Log.Infof("Preparing payloads in memory")

	var wgEnd sync.WaitGroup
	var wgStart sync.WaitGroup
	var payloads []*types.Payload

	for id, payloadName := range params.Payloads {
		payload, err := PreparePayload(params.DirPayloads, payloadName, int64(id))
		if err != nil {
			log.Log.Errorf("Cannot parse payload")
		}
		payloads = append(payloads, payload)
	}

	wgStart.Add(1)
	startTime := time.Now()

	// start bench to every host at given lambda with that payload
	for nodeId, host := range params.Hosts {
		log.Log.Infof("Benchmarking machine %s", host)

		wgEnd.Add(1)
		go StartBenchmarkSingleMachine(&wgEnd, &wgStart, &startTime, int64(nodeId), host, trafficModel, &payloads, params)
	}

	// start all threads at the same time
	wgStart.Done()

	// wait for all threads to stop
	wgEnd.Wait()

}

func StartBenchmarkLambdaRange(lambdaRange []float64, lambdaDelta float64, params *types.BenchmarkBasicParams) {
	// preliminary checks
	if lambdaRange == nil || len(lambdaRange) == 0 {
		log.Log.Errorf("lambdas is nil")
		return
	}

	if params.Hosts == nil || len(params.Hosts) == 0 {
		log.Log.Errorf("hosts is nil or 0")
		return
	}

}

/*
 * Single machines
 */

// StartBenchmarkSingleMachine start the benchmark for a given machine, if more than one payload is passed then they will
// be mixed according the percentage passed in params
func StartBenchmarkSingleMachine(wgEnd *sync.WaitGroup, wgStart *sync.WaitGroup, startTime *time.Time, nodeId int64, host string, trafficModel traffic.Model, payloads *[]*types.Payload, params *types.BenchmarkBasicParams) {
	// add to global wg
	utils.JoinWaitGroup.Add(1)

	// reset the learner
	if params.Learning {
		err := learning.LearnerReset(host, params.LearnerPort)
		if err != nil {
			log.Log.Fatalf("Cannot reset the learner, this is fatal")
		}
	}

	// wait for starting
	wgStart.Wait()

	functionUrl := fmt.Sprintf("http://%s:%d/function/%s", host, params.SchedulerPort, params.FunctionName)

	var payloadToUse *types.Payload
	reqId := int64(0)
	lambda := 1.0

	// loop until the time ends
	for {
		lambda = trafficModel.GetLoadAt(int(nodeId), float64(time.Now().UnixMilli()-startTime.UnixMilli())/1000)

		// decide the payload to use
		if len(*payloads) > 0 {
			// then we have to mix them
			rand.Seed(time.Now().UnixNano())
			pickedFloat := rand.Float64()

			// set the last
			payloadToUse = (*payloads)[len(*payloads)-1]
			cumulativePercentage := 0.0

			for i, percentage := range params.PayloadMixPercentages {
				cumulativePercentage = cumulativePercentage + percentage

				if pickedFloat < cumulativePercentage {
					payloadToUse = (*payloads)[i]
					break
				}
			}
		}

		var result = &types.BenchmarkResult{
			NodeId:       fmt.Sprintf("%d", nodeId),
			ReqId:        reqId,
			RequestsRate: lambda,
			PayloadName:  payloadToUse.Name,
		}

		log.Log.Debugf("[Tn%st%d] Starting request with lambda %f", result.NodeId, result.ReqId, result.RequestsRate)

		requestStartTime := time.Now()

		// do the request at given lambda
		go DoRequest(reqId, functionUrl, nodeId, payloadToUse, params, result)
		requestEndTime := time.Now()

		// generate time to wait
		waitTimeGenerated := 1 / lambda

		if params.TrafficGenerationDistribution == types.TrafficGenerationDistributionPoisson {
			waitTimeGenerated = rand.ExpFloat64() / lambda
			toCutAt := 0.01
			for {
				if waitTimeGenerated >= toCutAt {
					break
				}
				waitTimeGenerated = rand.ExpFloat64() / lambda
			}
		}

		// compute time to wait
		requestElapsed := (float64(requestEndTime.UnixMicro()) - float64(requestStartTime.UnixMicro())) / (1000.0 * 1000.0)
		if requestElapsed > waitTimeGenerated {
			log.Log.Warning("[T%s] Cannot generate request at the desired rate", fmt.Sprintf("n%dt%d", nodeId, reqId))
		}

		time.Sleep(time.Duration(waitTimeGenerated*1e9) - (requestEndTime.Sub(requestStartTime)))

		// check if benchmarkTimeElapsed
		if time.Now().Unix()-startTime.Unix() >= int64(params.BenchmarkTime) {
			log.Log.Infof("Benchmark time elapsed!")
			break
		}

		reqId = reqId + 1
	}

	// test end
	wgEnd.Done()

	// add to global wg
	utils.JoinWaitGroup.Done()
}

func DoRequest(reqId int64, url string, nodeId int64, payload *types.Payload, params *types.BenchmarkBasicParams, result *types.BenchmarkResult) {
	// add to global wg
	utils.JoinWaitGroup.Add(1)

	// log.Log.Debugf("Performing request to %s", url)

	startTime := time.Now()
	result.TypeId = payload.Id
	result.TimestampStart = startTime

	tracingId := fmt.Sprintf("n%dt%d", nodeId, reqId)
	headers := []utils.HttpHeader{
		{Key: utils.HttpLearnerServiceHeaderKeyTaskType, Value: fmt.Sprintf("%d", payload.Id)},
		{Key: utils.HttpLearnerServiceHeaderKeyTaskTracingId, Value: tracingId},
	}

	// do the request
	res, err := utils.HttpPostWithHeaders(url, payload.Binary, payload.Mime, headers)
	if err != nil {
		log.Log.Errorf("[T%s] Cannot do post request: %s", tracingId, err)

		result.RequestNetError = types.ERROR_REQUEST_GENERIC
		result.RequestNetErrorMessage = err.Error()
		result.TimestampEnd = time.Now()

		if os.IsTimeout(err) {
			result.RequestNetError = types.ERROR_REQUEST_TIMEOUT
		}

		err = db.LogJobEnd(result)
		if err != nil {
			log.Log.Errorf("[T%s] Cannot log job end: %s", tracingId, err)
		}

		// done to global wg
		utils.JoinWaitGroup.Done()

		return
	}

	result.ResponseStatusCode = int64(res.StatusCode)
	result.TimestampEnd = time.Now()
	result.TimeTotal = float64(result.TimestampEnd.Sub(result.TimestampStart).Microseconds()) / (1000.0 * 1000.0)

	log.Log.Debugf("[T%s] Performed request to %s: done time=%f", tracingId, url, result.TimeTotal)

	// parse timings headers
	parseTimingHeaders(&res.Header, result)

	var resBytes []byte
	if result.ResponseStatusCode == int64(500) {
		// parse the error code
		resBytes, err = ioutil.ReadAll(res.Body)
		if err != nil {
			log.Log.Errorf("[T%s] Cannot parse response body for error: result.ResponseStatusCode=%d err=%v body=%s headers=%v", tracingId, result.ResponseStatusCode, err, string(resBytes), res.Header)
		} else {
			resError := types.ResponseError{}
			err = json.Unmarshal(resBytes, &resError)
			if err != nil {
				log.Log.Errorf("[T%s] Cannot unmarshal response body for error: result.ResponseStatusCode=%d e=%v body=%s headers=%v", tracingId, result.ResponseStatusCode, err, string(resBytes), res.Header)
			}
			result.ResponseErrorCode = resError.Code
		}
	}

	// close response body
	_ = res.Body.Close()

	// compute the reward
	if params.Learning || params.LearningSetReward {
		result.LearningReward = learning.RewardFromDeadline(result, params.LearningRewardDeadlines)
	}

	// trigger learning if needed
	if params.Learning {

		result.LearningParsed = true
		err = parseLearningHeaders(&res.Header, result)
		if err != nil {
			log.Log.Fatalf("[T%s] Cannot parse learning headers res.StatusCode=%v result.ResponseErrorCode=%v e=%s url=%s res.body=%s", tracingId, res.StatusCode, result.ResponseErrorCode, err, url, string(resBytes))
		}

		// log to learner
		learningEntry := types.LearningEntry{
			Eid:    result.LearningEid,
			State:  result.LearningState,
			Action: result.LearningAction,
			Reward: result.LearningReward,
		}
		err = learning.LearnerBatchTrain(params.Hosts[nodeId], params.LearnerPort, &learningEntry, params)
		if err != nil {
			log.Log.Errorf("[T%s] Cannot post result to learner: %s", tracingId, err)
		}
	}

	// log to db the result
	err = db.LogJobEnd(result)
	if err != nil {
		log.Log.Errorf("[T%s] Cannot log job end: %s", tracingId, err)
	}

	// done to global wg
	utils.JoinWaitGroup.Done()
}

func parseTimingHeaders(headers *http.Header, result *types.BenchmarkResult) {
	var err error

	totalTimes := []float64{}
	schedulingTimes := []float64{}
	probingTimes := []float64{}
	peersListIp := []string{}

	totalTime := headers.Get(RES_HEADER_TOTAL_TIME_LIST)
	schedulingTime := headers.Get(RES_HEADER_SCHEDULING_TIME_LIST)
	probingTime := headers.Get(RES_HEADER_PROBING_TIME_LIST)
	executionTime := headers.Get(RES_HEADER_EXECUTION_TIME)
	externallyExecuted := headers.Get(RES_HEADER_EXTERNALLY_EXECUTED)
	peersListIpHeader := headers.Get(RES_HEADER_PEERS_LIST_IP)

	if totalTime != "" {
		err = json.Unmarshal([]byte(totalTime), &totalTimes)
		if err != nil {
			log.Log.Errorf("Cannot parse totalTime header: %s", totalTime)
		}
		result.TimesService = totalTimes
	}
	if schedulingTime != "" {
		err = json.Unmarshal([]byte(schedulingTime), &schedulingTimes)
		if err != nil {
			log.Log.Errorf("Cannot parse schedulingTime header: %s", schedulingTime)
		}
		result.TimesScheduling = schedulingTimes
	}
	if probingTime != "" {
		err = json.Unmarshal([]byte(probingTime), &probingTimes)
		if err != nil {
			log.Log.Errorf("Cannot parse probingTime header: %s", probingTime)
		}
		result.TimesProbing = probingTimes
	}

	if executionTime != "" {
		result.TimeExecution, err = strconv.ParseFloat(executionTime, 64)
		if err != nil {
			log.Log.Errorf("Cannot parse time header: %s", probingTime)
		}
	}

	if peersListIpHeader != "" {
		err = json.Unmarshal([]byte(peersListIpHeader), &peersListIp)
		if err != nil {
			log.Log.Errorf("Cannot parse peersListIp header: %s", probingTime)
		}
		result.PeersListIp = peersListIp
	}

	if externallyExecuted == "True" {
		result.ExternallyExecuted = true
	}

	result.TimesParsed = true
}

func parseLearningHeaders(headers *http.Header, result *types.BenchmarkResult) error {
	state := headers.Get(RES_HEADER_SCHEDULER_LEARNING_STATE)
	action := headers.Get(RES_HEADER_SCHEDULER_LEARNING_ACTION)
	eps := headers.Get(RES_HEADER_SCHEDULER_LEARNING_EPS)
	eid := headers.Get(RES_HEADER_SCHEDULER_LEARNING_EID)

	if state != "" {
		result.LearningState = state
	} else {
		return fmt.Errorf("state is blank, error in the server? headers=%v", headers)
	}

	if action != "" {
		result.LearningAction = action
	} else {
		return fmt.Errorf("action is blank, error in the server? headers=%v", headers)
	}

	if eps != "" {
		result.LearningEpsilon, _ = strconv.ParseFloat(eps, 64)
	} else {
		return fmt.Errorf("eps is blank, error in the server? headers=%v", headers)
	}

	if eid != "" {
		result.LearningEid = eid
	} else {
		return fmt.Errorf("eid is blank, error in the server? headers=%v", headers)
	}

	return nil
}
