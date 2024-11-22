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
	"io/ioutil"
	"scheduler/log"
	"scheduler/utils"
	"strconv"
)

const headerLearningEid = "X-P2pfaas-Learning-Eid"
const headerLearningState = "X-P2pfaas-Learning-State"
const headerLearningAction = "X-P2pfaas-Learning-Action"
const headerLearningReward = "X-P2pfaas-Learning-Reward"

const headerEpsilon = "X-P2pfaas-Eps"

func Act(entry *EntryAct) (*EntryActOutput, error) {
	var err error
	actOutput := EntryActOutput{}

	headers := []utils.HttpHeader{
		{Key: headerLearningState, Value: prepareStateString(entry.State)},
	}
	res, err := utils.HttpGetWithHeaders(getApiUrlAct(), headers)
	if err != nil {
		log.Log.Error("Cannot get the action from learning service at %s", getApiUrlAct())
		return nil, err
	}

	response, _ := ioutil.ReadAll(res.Body)
	_ = res.Body.Close()

	// parse action
	responseString := string(response)
	actOutput.Action, err = strconv.ParseFloat(responseString, 64)
	if err != nil {
		return nil, err
	}

	// parse headers
	eps := res.Header.Get(headerEpsilon)
	if eps != "" {
		actOutput.Eps, err = strconv.ParseFloat(eps, 64)
	}

	return &actOutput, nil
}

func Train(entry *EntryLearning) error {
	headers := []utils.HttpHeader{
		{Key: headerLearningEid, Value: fmt.Sprintf("%d", entry.Eid)},
		{Key: headerLearningState, Value: prepareStateString(entry.State)},
		{Key: headerLearningAction, Value: fmt.Sprintf("%.4f", entry.Action)},
		{Key: headerLearningReward, Value: fmt.Sprintf("%.4f", entry.Reward)},
	}
	res, err := utils.HttpGetWithHeaders(getApiUrlTrain(), headers)
	if err != nil {
		log.Log.Error("Cannot get the action from learning service at %s", getApiUrlTrain())
		return err
	}

	if res.StatusCode != 200 {
		return fmt.Errorf("failed train call")
	}

	return nil
}
