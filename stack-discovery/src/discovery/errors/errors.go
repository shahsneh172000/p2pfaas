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

// Package errors implements error management
package errors

import (
	"encoding/json"
	"io"
	"net/http"
)

type ErrorReply struct {
	Code    int    `json:"code,omitempty"`
	Message string `json:"message,omitempty"`
}

const (
	GenericError         int = 1
	DBError              int = 2
	GenericNotFoundError int = 3
	InputNotValid        int = 4
	// configuration
	ConfigurationNotReady int = 100
	// mongo errors
	DBDuplicateKey int = 11000
)

var errorMessages = map[int]string{
	1: "Generic Error",
	2: "DB Error",
	3: "Not Found",
	4: "Passed input is not correct or malformed",
	// configuration
	100: "Configuration not ready",
	// mongo
	11000: "A key is duplicated",
}

var errorStatus = map[int]int{
	1: 500,
	2: 500,
	3: 404,
	4: 400,
	// configuration
	100: 500,
	// mongo
	11000: 400,
}

func ReplyWithError(w http.ResponseWriter, errorCode int) {
	w.WriteHeader(errorStatus[errorCode])
	var errorReply = ErrorReply{Code: errorCode, Message: errorMessages[errorCode]}
	errorReplyJSON, _ := json.Marshal(errorReply)
	io.WriteString(w, string(errorReplyJSON))
}

func ReplyWithErrorMessage(w http.ResponseWriter, errorCode int, msg string) {
	w.WriteHeader(errorStatus[errorCode])
	var errorReply = ErrorReply{Code: errorCode, Message: msg}
	errorReplyJSON, _ := json.Marshal(errorReply)
	io.WriteString(w, string(errorReplyJSON))
}
