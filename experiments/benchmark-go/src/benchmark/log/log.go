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

package log

import (
	"github.com/op/go-logging"
	"os"
)

var logEnv = "production"

// Log is the main object for accessing logging services
var Log = logging.MustGetLogger("benchmarker")

var logTerminalFormat = logging.MustStringFormatter(
	`%{color}%{time} %{level:.4s}/%{shortpkg}.%{shortfunc}%{color:reset} %{message}`,
)
var logTerminalProductionFormat = logging.MustStringFormatter(
	`%{time} %{shortfunc} > %{level:.4s} %{id:03x} %{message}`,
)

func init() {
	SetDebug(true)
	// stdoutBackend := logging.NewLogBackend(os.Stdout, "", 0)
	// stderrBackend := logging.NewLogBackend(os.Stderr, "", 0)

	// if os.Getenv("P2PFAAS_LOG_ENV") == "development" {
	//	logEnv = "development"
	// }
	// in production no color and level error
	// if logEnv == "production" {
	//	stderrBackendFormatted := logging.NewBackendFormatter(stderrBackend, logTerminalProductionFormat)
	//	stderrBackendLeveled := logging.AddModuleLevel(stderrBackendFormatted)
	//	stderrBackendLeveled.SetLevel(logging.INFO, "")
	//	logging.SetBackend(stderrBackendLeveled)
	//} else {
	// stdoutBackendFormatted := logging.NewBackendFormatter(stdoutBackend, logTerminalFormat)
	// logging.SetBackend(stdoutBackendFormatted) // if production put stderrBackendLeveled
	//}

	// Log.Infof("Logging init successfully with env: %s", logEnv)

	// Log.Debugf("debug")
	// Log.Info("info")
	// Log.Notice("notice")
	// Log.Warning("warning")
	// Log.Error("err")
	// Log.Critical("crit")

}

func SetDebug(enabled bool) {
	stdoutBackend := logging.NewLogBackend(os.Stdout, "", 0)

	var stdoutBackendFormatted logging.Backend
	stdoutBackendFormatted = logging.NewBackendFormatter(stdoutBackend, logTerminalFormat)

	if !enabled {
		stderrBackendLeveled := logging.AddModuleLevel(stdoutBackendFormatted)
		stderrBackendLeveled.SetLevel(logging.INFO, "")
		stdoutBackendFormatted = stderrBackendLeveled
	}

	logging.SetBackend(stdoutBackendFormatted) // if production put stderrBackendLeveled
}

func GetEnv() string {
	return logEnv
}
