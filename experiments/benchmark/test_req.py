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

import requests
import time
import mimetypes
import logging
from threading import Thread
from io import BytesIO
from PIL import Image

OVERHEAD = 2.488 - 0.122
URL = "http://192.168.50.100:18080/function/fn-pigo"
# URL = "http://localhost:18080/dev/http/post"
# PAYLOAD = "./2021_nca_postprint.pdf"
PAYLOAD = "./blobs/familyr_320p.jpg"


def read_binary(uri):
    if uri == "" or uri is None:
        return None

    in_file = open(uri, "rb")  # opening for [r]eading as [b]inary
    data = in_file.read()  # if you only wanted to read 512 bytes, do .read(512)
    in_file.close()

    return data


# logging.basicConfig(level=logging.DEBUG)
s = requests.Session()

payload_bin = read_binary(PAYLOAD)
payload_mime = mimetypes.guess_type(PAYLOAD)[0]

delays = []  # ms

for i in range(100):
    time_start = time.time()

    headers = {
        'Content-Type': payload_mime,
        'Connection': 'Keep-Alive'
    }
    res = s.post(URL, data=payload_bin, headers=headers, timeout=30)

    time_end = time.time()

    delays.append((time_end - time_start) * 1000.0)

    print(
        f"Req#{i}: statusCode={res.status_code}, elapsed={(time_end - time_start) * 1000.0:.3f}ms, elapsedTrue={(time_end - time_start) * 1000.0 - OVERHEAD :.3f}ms")

    # time.sleep(5)

s.close()

print()
print(f"Average delay {sum(delays) / len(delays)}ms")
