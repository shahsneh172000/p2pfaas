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

package learning

import (
	"benchmark/log"
	"benchmark/types"
	"benchmark/utils"
	json2 "encoding/json"
	"fmt"
	"sync"
)

var learningEntries = make(map[string]*[]*types.LearningEntry)
var learningEntriesMutex = sync.Mutex{}

func LearnerBatchTrain(host string, port uint64, entry *types.LearningEntry, params *types.BenchmarkBasicParams) error {
	log.Log.Debugf("Added entry for batch learning: host=%s entry=%v", host, entry)

	if host == "" {
		log.Log.Fatalf("host is a blank string")
	}

	learningEntriesMutex.Lock()
	entries, exists := learningEntries[host]

	if !exists {
		learningEntries[host] = &[]*types.LearningEntry{entry}
		learningEntriesMutex.Unlock()
		return nil
	}

	// add to list
	newEntries := append(*entries, entry)
	learningEntries[host] = &newEntries

	log.Log.Debugf("host=%s entries=%d batch_size=%d", host, len(newEntries), params.LearningBatchSize)

	// do the train if len is reached
	if uint64(len(newEntries)) >= params.LearningBatchSize {
		log.Log.Debugf("host=%s entries=%d batch_size=%d starting train!", host, len(newEntries), params.LearningBatchSize)

		learningEntries[host] = &[]*types.LearningEntry{}
		learningEntriesMutex.Unlock()

		err := learnerTrainBatch(host, port, &newEntries)
		if err != nil {
			log.Log.Errorf("Cannot do the call for batch learning to host=%s e=%s", host, err)
			return err
		}

		return nil
	}

	learningEntriesMutex.Unlock()

	return nil
}

func learnerTrainBatch(host string, port uint64, entries *[]*types.LearningEntry) error {
	url := fmt.Sprintf("http://%s:%d/train_batch", host, port)
	jsonBytes, err := json2.Marshal(entries)

	log.Log.Debugf("Post to learner len(entries)=%s url=%s json=%s", len(*entries), url, string(jsonBytes))

	// do the post
	res, err := utils.HttpPost(url, jsonBytes, "application/json")
	if err != nil {
		log.Log.Errorf("Cannot do post to %s: err=%s", url, err)
		return err
	}

	_ = res.Body.Close()

	if res.StatusCode != 200 {
		log.Log.Errorf("Post to learner url=%s resultCode=%d batchSize=%d json=%s", url, res.StatusCode, len(*entries), string(jsonBytes))
		return fmt.Errorf("call to learner statusCode=%d", res.StatusCode)
	}

	return nil
}

func learnerTrainSingle(hostIp string, learnerPort uint64, result *types.BenchmarkResult) error {
	url := fmt.Sprintf("http://%s:%d/train", hostIp, learnerPort)

	var headers = []utils.HttpHeader{
		{Key: HEADER_LEARNING_EID, Value: result.LearningEid},
		{Key: HEADER_LEARNING_STATE, Value: result.LearningState},
		{Key: HEADER_LEARNING_ACTION, Value: result.LearningAction},
		{Key: HEADER_LEARNING_REWARD, Value: fmt.Sprintf("%.4f", result.LearningReward)},
	}
	// do the post
	res, err := utils.HttpGetWithHeaders(url, headers)
	if err != nil {
		return err
	}

	_ = res.Body.Close()

	log.Log.Debugf("Get to learner resultCode=%d", res.StatusCode)

	return nil
}

func LearnerReset(hostIp string, learnerPort uint64) error {
	url := fmt.Sprintf("http://%s:%d/learner/reset", hostIp, learnerPort)

	// do the post
	res, err := utils.HttpGet(url)
	if err != nil {
		return err
	}

	_ = res.Body.Close()

	log.Log.Debugf("Get to learner resultCode=%d", res.StatusCode)

	return nil
}
