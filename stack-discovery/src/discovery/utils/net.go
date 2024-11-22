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

package utils

import (
	"discovery/log"
	"net"
	"strings"
)

type IPError struct{}

func (e IPError) Error() string {
	return "Could not get ip address"
}

func GetInternalIP(ifaceName string) (string, error) {
	iface, err := net.InterfaceByName(ifaceName)
	if err != nil {
		log.Log.Errorf("Could not find interface \"%s\"", ifaceName)
		return "", IPError{}
	}
	if iface.Flags&net.FlagUp == 0 {
		log.Log.Errorf("Interface \"%s\" is down", ifaceName)
		return "", IPError{} // interface down
	}
	if iface.Flags&net.FlagLoopback != 0 {
		log.Log.Errorf("Interface \"%s\" is loopback", ifaceName)
		return "", IPError{} // loopback interface
	}

	addresses, err := iface.Addrs()

	for _, addr := range addresses {
		var ip net.IP
		switch v := addr.(type) {
		case *net.IPNet:
			ip = v.IP
		case *net.IPAddr:
			ip = v.IP
		}
		if ip == nil || ip.IsLoopback() {
			continue
		}
		ip = ip.To4()
		if ip == nil {
			continue // not an ipv4 address
		}
		return ip.String(), nil
	}

	log.Log.Errorf("Could not get ip for \"%s\"", ifaceName)
	return "", IPError{}
}

/*
 * Generic utils
 */

func IsolateIPFromPort(ip string) string {
	lastColon := strings.LastIndex(ip, ":")
	if lastColon == -1 {
		return ip
	}
	trueIp := ip[0:lastColon]
	return trueIp
}
