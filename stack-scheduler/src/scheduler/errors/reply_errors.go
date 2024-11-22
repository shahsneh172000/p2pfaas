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

package errors

import (
	"encoding/json"
	"net/http"
	"scheduler/utils"
)

type ErrorReply struct {
	Code    int    `json:"code,omitempty"`
	Message string `json:"message,omitempty"`
	Err     error  `json:"err,omitempty"`
}

const (
	GenericError                int = 1
	DBError                     int = 2
	GenericNotFoundError        int = 3
	InputNotValid               int = 4
	FaasConnectError            int = 5
	MarshalError                int = 6
	ServiceNotValid             int = 100
	GenericDeployError          int = 200
	GenericOpenFaasError        int = 300
	JobCannotBeScheduledError   int = 400
	JobDeliberatelyRejected     int = 401
	CannotRetrieveAction        int = 402
	JobCouldNotBeForwarded      int = 403
	PeerResponseNil             int = 404
	CannotRetrieveRecipientNode int = 405

	DBDuplicateKey int = 11000
)

var errorMessages = map[int]string{
	1: "Generic Error",
	2: "DB Error",
	3: "Not Found",
	4: "Passed input is not correct or malformed",
	5: "Could not contact OpenFaaS backend",
	6: "Cannot marshal the struct",
	// service validation
	100: "Passed service is not valid",
	// deploy
	200: "Error while deploying the service",
	// openfaas
	300: "OpenFaas generic error, see logs",
	// scheduler
	400: "Job cannot be scheduled due to physical limitation (e.g. queue full)",
	401: "Job have been deliberately rejected by the scheduler",
	402: "It is not possible to retrieve the scheduling action",
	403: "It was not possible to forward the request to the neighbor",
	404: "Peer replied with nil response",
	405: "Recipient node to which the job must be forwarded cannot be retrieved",
	// mongo
	11000: "A key is duplicated",
}

var errorStatus = map[int]int{
	1: 500,
	2: 500,
	3: 404,
	4: 400,
	5: 500,
	6: 500,
	// service validation
	100: 400,
	// deploy
	200: 500,
	// openfaas
	300: 500,
	// scheduler
	400: 500,
	401: 503,
	402: 500,
	403: 500,
	404: 500,
	405: 500,
	// mongo
	11000: 400,
}

func GetErrorJson(errorCode int) (int, string, error) {
	var errorReply = ErrorReply{Code: errorCode, Message: errorMessages[errorCode]}
	errorReplyJSON, err := json.Marshal(errorReply)

	if err != nil {
		return -1, "", err
	}

	return errorStatus[errorCode], string(errorReplyJSON), nil
}

func GetErrorJsonMessage(errorCode int, msg string) (int, string, error) {
	var errorReply = ErrorReply{Code: errorCode, Message: msg}
	errorReplyJSON, err := json.Marshal(errorReply)

	if err != nil {
		return -1, "", err
	}

	return errorStatus[errorCode], string(errorReplyJSON), nil
}

func ReplyWithError(w *http.ResponseWriter, errorCode int, customHeaders *map[string]string) {
	errorStatusCode, errorResponseJson, _ := GetErrorJson(errorCode)

	utils.HttpSendJSONResponse(w, errorStatusCode, errorResponseJson, customHeaders)
}

func ReplyWithErrorMessage(w *http.ResponseWriter, errorCode int, msg string, customHeaders *map[string]string) {
	var errorReply = ErrorReply{Code: errorCode, Message: msg}
	errorReplyJSON, _ := json.Marshal(errorReply)

	utils.HttpSendJSONResponse(w, errorStatus[errorCode], string(errorReplyJSON), customHeaders)
}
