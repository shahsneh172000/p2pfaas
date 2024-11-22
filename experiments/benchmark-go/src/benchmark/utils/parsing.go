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

package utils

import (
	"benchmark/log"
	"bufio"
	"io"
	"io/ioutil"
	"os"
	"strconv"
	"strings"
)

func ParseArrayFloat64FromString(arrayStr string) ([]float64, error) {
	var err error
	lambdaArray := []float64{}

	if arrayStr != "" {
		lambdaArraySArr := strings.Split(arrayStr, ",")
		lambdaArray, err = ParseArrayFloat64(lambdaArraySArr)
		if err != nil {
			log.Log.Errorf("Cannot parse array lambdaArraySArr=%s: %s", lambdaArraySArr, err)
			return nil, err
		}
	}

	return lambdaArray, nil
}

func ParseArrayFloat64(arr []string) ([]float64, error) {
	var out []float64

	for _, v := range arr {
		vFloat, err := strconv.ParseFloat(v, 64)
		if err != nil {
			log.Log.Errorf("Cannot parse float %s", v)
			return nil, err
		}

		out = append(out, vFloat)
	}

	return out, nil
}

func ParseArrayStringFromFile(filePath string) ([]string, error) {
	var fileLines []string

	readFile, err := os.Open(filePath)
	if err != nil {
		log.Log.Errorf("Cannot open file: %s", err)
	}

	fileScanner := bufio.NewScanner(readFile)
	fileScanner.Split(bufio.ScanLines)

	// scan lines
	for fileScanner.Scan() {
		fileLines = append(fileLines, strings.TrimSpace(fileScanner.Text()))
	}

	err = readFile.Close()
	if err != nil {
		return nil, err
	}

	return fileLines, err
}

func ReadFileToBytes(filePath string) ([]byte, string, error) {
	f, _ := os.Open(filePath)

	data, err := ioutil.ReadAll(f)
	if err != nil {
		return nil, "", err
	}

	_, err = f.Seek(0, io.SeekStart)
	if err != nil {
		return nil, "", err
	}

	contentType, err := FileGetContentType(f)
	if err != nil {
		return nil, "", err
	}

	return data, contentType, nil
}
