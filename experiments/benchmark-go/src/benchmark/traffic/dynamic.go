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

package traffic

import (
	"benchmark/log"
	"benchmark/utils"
	"fmt"
	"math"
	"strconv"
	"strings"
)

const modelDynamicName = "ModelDynamic"

type ModelDynamic struct {
	init bool

	dir               string
	filenamePrefix    string
	filenameExtension string
	nodesCount        int64

	MinLoad     float64
	MaxLoad     float64
	TotalTime   float64
	Shift       float64
	Repetitions float64

	loadPointsSize  map[int]int
	loadScaleFactor map[int]float64
	loadPoints      map[int][]float64
}

func (m *ModelDynamic) Init() error {

	for i := 0; i < int(m.nodesCount); i++ {
		log.Log.Debugf("Parsing traffic model file %d", i)

		loadPoints, err := m.parseLoadFile(i)
		if err != nil {
			log.Log.Errorf("Cannot parse load file: %s", err)
			return err
		}
		m.loadPointsSize[i] = len(loadPoints)
		m.loadPoints[i] = loadPoints
		m.loadScaleFactor[i] = m.TotalTime / float64(m.loadPointsSize[i])

		log.Log.Infof("Model init for node %d: loadPointsSize=%d loadScaleFactor=%f", i, m.loadPointsSize[i], m.loadScaleFactor[i])
	}

	m.init = true

	return nil
}

func (m ModelDynamic) GetLoadAt(nodeIndex int, time float64) float64 {
	if !m.init {
		log.Log.Errorf("Model is not initialized!")
		return 0.0
	}

	// find the entry id in the array of loads
	timeAdjust := (time + m.Shift) / (m.loadScaleFactor[nodeIndex] / m.Repetitions)
	timeNormalizedDivision := timeAdjust / float64(m.loadPointsSize[nodeIndex])

	reminder := timeAdjust - (math.Floor(timeNormalizedDivision) * float64(m.loadPointsSize[nodeIndex]))
	reminderDecimal := reminder - float64(int(math.Floor(reminder)))

	intervalUp := int(math.Ceil(reminder)) % m.loadPointsSize[nodeIndex]
	intervalDown := int(math.Floor(reminder)) % m.loadPointsSize[nodeIndex]

	if intervalDown == intervalUp {
		intervalUp = (intervalUp + 1) % m.loadPointsSize[nodeIndex]
	}

	// log.Log.Debugf("time=%f m.loadScaleFactor[nodeIndex]=%f timeNormalizedDivision=%f reminder=%f intervalDown=%d intervalUp=%d", time, m.loadScaleFactor[nodeIndex], timeNormalizedDivision, reminder, intervalDown, intervalUp)

	pureLoad := m.loadPoints[nodeIndex][intervalDown] + (m.loadPoints[nodeIndex][intervalUp]-m.loadPoints[nodeIndex][intervalDown])*reminderDecimal

	return m.MinLoad + (m.MaxLoad-m.MinLoad)*pureLoad
}

func (m ModelDynamic) parseLoadFile(nodeIndex int) ([]float64, error) {
	var err error
	var lines []string
	var load float64

	filePath := fmt.Sprintf("%s/%s%d.%s", m.dir, m.filenamePrefix, nodeIndex, m.filenameExtension)
	log.Log.Debugf("Parsing file path %s", filePath)

	lines, err = utils.ParseArrayStringFromFile(filePath)
	if err != nil {
		log.Log.Errorf("Cannot parse load file for node %d", nodeIndex)
		return nil, err
	}

	loadPoints := []float64{}

	// parse time and load
	for _, line := range lines {
		// log.Log.Debugf("Load line: %s", line)
		components := strings.Split(line, ",")

		load, err = strconv.ParseFloat(components[1], 64)
		if err != nil {
			log.Log.Errorf("Cannot parse float %s", err)
			return nil, err
		}

		loadPoints = append(loadPoints, load)
	}

	return loadPoints, nil
}

func (m ModelDynamic) GetName() string {
	return modelDynamicName
}

/*
 * Creation
 */

func CreateModelDynamic(dir string, filenamePrefix string, filenameExtension string, nodesCount int64, minLoad float64, maxLoad float64, totalTime float64, shift float64, repetitions float64) *ModelDynamic {
	return &ModelDynamic{
		dir:               dir,
		filenamePrefix:    filenamePrefix,
		filenameExtension: filenameExtension,
		nodesCount:        nodesCount,

		TotalTime:   totalTime,
		Shift:       shift,
		Repetitions: repetitions,
		MinLoad:     minLoad,
		MaxLoad:     maxLoad,

		loadPoints:      make(map[int][]float64),
		loadPointsSize:  make(map[int]int),
		loadScaleFactor: make(map[int]float64),

		init: false,
	}
}
