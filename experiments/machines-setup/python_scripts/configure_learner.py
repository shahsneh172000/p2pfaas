import getopt
import json
import sys

import requests

from common import status_str

SERVICE_PORT = 19020
API_CONFIGURATION_URL = "learner/parameters"

ips = []

LAMDBAS = [2.0, 3.0, 6.0, 6.5, 7.0, 8.0, 2.0, 3.0, 6.0, 6.5, 7.0, 8.0]


def prepare_payload_sarsa_q_table(node_i):
    def decay(end_time, decay_end, decay_start, l):
        return pow(decay_end, (decay_end / decay_start) / (end_time * l))

    payload = {
        "actions_n": 3 + 11,  # reject, execute, probe-and-forward, forward to 1,2,3,4,5,6,7,8,9,10,11
        "alpha": 0.001,
        "beta": 0.1,
        "window_size": 10,
        "epsilon": 0.9,
        "epsilon_min": 0.05,
        "epsilon_decay": 0.9995,  # decay(4000, 0.05, 0.9, LAMDBAS[node_i]),  # 0.999,
        "epsilon_decay_enabled": True,
        "entry_missing_max_attempts": 50
    }
    return json.dumps(payload)


def set_configuration(host_ip, parameters_dict):
    # prepare request
    url = f"http://{host_ip}:{SERVICE_PORT}/{API_CONFIGURATION_URL}"
    headers = {'Content-Type': "application/json"}
    ok = True

    print(f"\r[{status_str.CHECK_STR}] {host_ip} configuring...", end="")
    try:
        res = requests.post(url, data=parameters_dict, headers=headers, timeout=5)
    except (requests.Timeout, requests.ConnectionError):
        print(f"\r[{status_str.DEAD_STR}] {host_ip} is not responding")
        ok = False

    if ok:
        print_str = status_str.OK_STR
        if res.status_code != 200:
            print_str = status_str.DEAD_STR

        print(f"\r[{print_str}] {host_ip} set with {parameters_dict} [{res.status_code}]")


def main(argv):
    hosts_file_path = ""
    host = ""

    usage = "configure_learner.py"

    try:
        opts, args = getopt.getopt(
            argv, "h", ["hosts-file=", "host="])
    except getopt.GetoptError as e:
        print(e)
        sys.exit(2)
    for opt, arg in opts:
        # print(opt + " -> " + arg)
        if opt == '-h':
            print(usage)
            sys.exit()
        elif opt in ["--hosts-file"]:
            hosts_file_path = arg
        elif opt in ["--host"]:
            host = arg

    parameters_dict = prepare_payload_sarsa_q_table(0)

    print("====== P2P-FAAS Machines Setup ======")
    print("> hosts-file %s" % hosts_file_path)
    print("> host %s" % host)
    print("> learner_params %s" % parameters_dict)

    if host != "" and hosts_file_path != "":
        print("Please specify host or hosts file")
        sys.exit(2)

    if hosts_file_path != "":
        conf_file = open(hosts_file_path, "r")

        for line in conf_file:
            if line[0] == "#":
                continue
            ips.append(line.strip())

        conf_file.close()

        # start requests
        for i in range(len(ips)):
            parameters_dict = prepare_payload_sarsa_q_table(i)
            set_configuration(ips[i], parameters_dict)

    if host != "":
        set_configuration(host, parameters_dict)

    print("\n> Done!")


if __name__ == "__main__":
    main(sys.argv[1:])
