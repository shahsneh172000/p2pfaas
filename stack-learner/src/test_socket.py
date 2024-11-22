#  P2PFaaS - A framework for FaaS Load Balancing
#  Copyright (c) 2019 - 2022. Gabriele Proietti Mattia <pm.gabriele@outlook.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.

import asyncio
import time

from websockets import connect


async def hello(uri):
    async with connect(uri) as websocket:
        time_start = time.time()

        await websocket.send("[1.0, 1.1]")
        message = await websocket.recv()

        time_end = time.time()

        print(f"Received message={message} time={time_end - time_start}")


if __name__ == '__main__':
    message_id = 0
    while True:
        asyncio.run(hello("ws://localhost:8765"))

        message_id += 1
        time.sleep(1)
