import json
import requests
import sys

from common import status_str

SERVICE_PORT = 19000
API_CONFIGURATION_URL = "configuration"
API_RESET_URL = "reset"

if (len(sys.argv) != 2):
    print("usage: configure-discovery.py discovery-file.txt")
    exit(1)

ips = []
ids = []


def prepare_payload(host_id, host_ip, init_servers):
    payload = {}
    payload["machine_ip"] = host_ip
    payload["machine_id"] = host_id
    payload["machine_group_name"] = "cluster00"
    payload["init_servers"] = init_servers
    # payload["poll_time"] = 120
    # payload["poll_timeout"] = 10
    return json.dumps(payload)


def set_configuration(host_id, host_ip, init_servers):
    # prepare request
    url = "http://{0}:{1}/{2}".format(host_ip, SERVICE_PORT, API_CONFIGURATION_URL)
    url_reset = "http://{0}:{1}/{2}".format(host_ip, SERVICE_PORT, API_RESET_URL)
    headers = {'Content-Type': "application/json"}
    ok = True

    print("\r[%s] %s configuring..." % (status_str.CHECK_STR, host_ip), end="")
    try:
        res = requests.get(url_reset)
        res = requests.post(url, data=prepare_payload(host_id, host_ip, init_servers), headers=headers, timeout=5)
    except (requests.Timeout, requests.ConnectionError):
        print("\r[%s] %s is not responding" % (status_str.DEAD_STR, host_ip))
        ok = False

    if ok:
        print_str = status_str.OK_STR
        if res.status_code != 200:
            print_str = status_str.DEAD_STR

        print("\r[%s] %s set as \"%s\" [%s]" % (print_str, host_ip, host_id, res.status_code))


conf_file_path = sys.argv[1]
if conf_file_path == "":
    print("Configuration path is empty")
    sys.exit(1)

conf_file = open(conf_file_path, "r")

for line in conf_file:
    if line[0] == "#":
        continue
    comp = line.split()
    host_ip = comp[1]
    host_id = comp[0]
    ips.append(host_ip)
    ids.append(host_id)

conf_file.close()

print("> got %d hosts\n" % len(ips))

# start requests
for i in range(len(ips)):
    set_configuration(ids[i], ips[i], [ips[0]])

print("\n> Done!")
