import json
import sys

import requests

from common import status_str

SERVICE_PORT = 18080
API_CONFIGURATION_URL = "configuration"

ips = []


def prepare_payload(max_functions, queue_len):
    payload = {
        "parallel_running_functions_max": int(max_functions),
        "queue_length_max": int(queue_len),
        "queue_enabled": False,
    }
    return json.dumps(payload)


def set_configuration(host_ip, max_functions, queue_len):
    k = int(max_functions)
    # prepare request
    url = "http://{0}:{1}/{2}".format(host_ip, SERVICE_PORT, API_CONFIGURATION_URL)
    headers = {'Content-Type': "application/json"}
    ok = True

    print("\r[%s] %s configuring..." % (status_str.CHECK_STR, host_ip), end="")
    try:
        res = requests.post(url, data=prepare_payload(max_functions, queue_len), headers=headers, timeout=5)
    except (requests.Timeout, requests.ConnectionError):
        print("\r[%s] %s is not responding" % (status_str.DEAD_STR, host_ip))
        ok = False

    if ok:
        print_str = status_str.OK_STR
        if res.status_code != 200:
            print_str = status_str.DEAD_STR

        print("\r[%s] %s set with k=%d [%s]" % (print_str, host_ip, k, res.status_code))


if len(sys.argv) != 4:
    print("usage: configure_scheduler_service hosts-file.txt 10")
    sys.exit(1)

hosts_file = sys.argv[1]
max_functions = sys.argv[2]
queue_len = sys.argv[3]

conf_file = open(hosts_file, "r")

for line in conf_file:
    if line[0] == "#":
        continue
    ips.append(line.strip())

conf_file.close()

print("> got %d hosts\n" % len(ips))
print("> got max_functions \"%s\"" % max_functions)
print("> got queue_len \"%s\"" % queue_len)

# start requests
for i in range(len(ips)):
    set_configuration(ips[i], max_functions, queue_len)

print("\n> Done!")
