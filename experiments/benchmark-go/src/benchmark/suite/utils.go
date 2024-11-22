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
	"benchmark/types"
	"benchmark/utils"
	"fmt"
)

func PreparePayload(payloadsDir string, payloadName string, id int64) (*types.Payload, error) {
	payloadPath := fmt.Sprintf("%s/%s", payloadsDir, payloadName)
	payloadBytes, payloadMime, err := utils.ReadFileToBytes(payloadPath)
	if err != nil {
		return nil, err
	}

	return &types.Payload{
		Id:     id,
		Name:   payloadName,
		Mime:   payloadMime,
		Binary: payloadBytes,
	}, nil
}
