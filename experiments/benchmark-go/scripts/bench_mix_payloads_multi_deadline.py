#!/usr/bin/env python3

from dataclasses import dataclass
import subprocess
import time


BENCHMARK_SCRIPT = "./benchmark"
TRAFFIC_GEOGRAPHIC = False

CONFIGURE_SCHEDULER_PWR_N = "../../machines-setup/python_scripts/configure_scheduler_pwr_n.sh 1"
CONFIGURE_SCHEDULER_LEARNING = "../../machines-setup/python_scripts/configure_scheduler_learning.sh"

PARAM_BENCH_TIME = 1800
TESTS = [
    (True, "0.18825", "0.07495"),
    (False, "0.18825", "0.07495"),

    (True, "0.19766", "0.07870"),
    (False, "0.19766", "0.07870"),

    (True, "0.20708", "0.08245"),
    (False, "0.20708", "0.08245"),

    (True, "0.21649", "0.08619"),
    (False, "0.21649", "0.08619"),

    (True, "0.22590", "0.08994"),
    (False, "0.22590", "0.08994"),

    (True, "0.23531", "0.09369"),
    (False, "0.23531", "0.09369"),

    (True, "0.24473", "0.09744"),
    (False, "0.24473", "0.09744"),
]


def build_cmdline(test=(True, "1.0", "1.0")):
    out = BENCHMARK_SCRIPT
    out += " " + "-hosts-file \"./hosts.txt\""
    out += " " + f"-benchmark-time \"{PARAM_BENCH_TIME}\""
    out += " " + "-function-name \"fn-pigo\""
    out += " " + "-dir-payloads \"./blobs\""
    out += " " + "-payloads \"familyr_320p.jpg,familyr_180p.jpg\""
    out += " " + "-payloads-mix-percentages \"0.50,0.50\""
    out += " " + "-dir-log \"./log\""
    out += " " + f"-learning-reward-deadlines \"{test[1]},{test[2]}\""
    out += " " + "-learning-set-reward"

    if TRAFFIC_GEOGRAPHIC:
        out += " " + "-traffic-model-dir \"./traffic\""
        out += " " + "-traffic-model-type \"dynamic\""
        out += " " + "-traffic-model-file-prefix \"traffic_node_\""
        out += " " + "-traffic-model-file-extension \"csv\""
        out += " " + "-traffic-model-shift \"0.0\""
        out += " " + "-traffic-model-repetitions \"3.0\""
        out += " " + "-traffic-model-min-load \"0.0\""
        out += " " + "-traffic-model-max-load \"20.0\""
        out += " " + "-traffic-generation-distribution \"deterministic\""
    else:
        out += " " + "-lambdas \"8,8.5,9,9.5,10,10.5,11,12,12.5,13,13.5,14\""
        out += " " + "-traffic-model-type \"static\""
        out += " " + "-traffic-generation-distribution \"poisson\""

    if test[0]:
        out += " " + "-learning-batch-size \"10\""
        out += " " + "-learning"

    return out

time_str = str(int(time.time()))

for test in TESTS:
    out_f = open(
        f"./bench_mix_payloads_multi_deadline_{time_str}.txt", "a")

    time_start = time.time()

    # set scheduler
    print(f"==> Setting scheduler for deadline {test}")

    process = subprocess.Popen(
        CONFIGURE_SCHEDULER_LEARNING if test[0] else CONFIGURE_SCHEDULER_PWR_N, stdout=subprocess.PIPE, shell=True, text=True)
    out, err = process.communicate()

    out_f.write(str(out))

    # sleep for 5 seconds
    print(f"==> Sleeping for 10 seconds")
    time.sleep(10)

    # start test
    cmdline = build_cmdline(test)
    print(f"==> Benchmark {test}, cmdline={cmdline}")
    process = subprocess.Popen(
        cmdline, stdout=subprocess.PIPE, shell=True, text=True)
    out, err = process.communicate()

    out_f.write(str(out))

    time_end = time.time()

    print(
        f"==> Benchmarking deadline {test}, elapsed={time_end-time_start:.3f}s\n")

    out_f.close()

    # sleep for 5 seconds
    print(f"==> Sleeping for 15 seconds")
    time.sleep(15)