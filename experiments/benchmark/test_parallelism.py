# the purpose of this script is to test the level of parallelism in the machine
import dataclasses
import time
from threading import Thread, Lock

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import t as t_student

from plot.utils import PlotUtils, Utils

N_PARALLELISM_TO = 24
N_TESTS = 10


@dataclasses.dataclass
class ThreadReturnValue:
    value: float


def cpu_bound_function():
    """Test function"""
    value_a = 1
    value_b = 1.1
    for i in range(5000000):
        value_a += 1
        value_b += 1 + 0.2
        # print(f"a={value_a} b={value_b}")


def test_thread(thread_id, return_value: ThreadReturnValue):
    # wait to start
    # start_mutex.acquire()
    # print(f"thread={thread_id} started")

    time_start = time.time()

    cpu_bound_function()

    time_total = time.time() - time_start
    # print(f"thread={thread_id} end: time={time_total:.2f}")

    return_value.value = time_total


results = {}  # { "parallelism" : [values] }

for test_id in range(N_TESTS):
    print(f"Starting test_id={test_id}")

    for parallelism in range(1, N_PARALLELISM_TO + 1):
        print(f"parallelism={parallelism} start")

        if parallelism not in results.keys():
            results[parallelism] = []

        threads = []
        return_values = [ThreadReturnValue(0.0) for i in range(parallelism)]

        for thread_id in range(parallelism):
            print(f"parallelism={parallelism} creating thread {thread_id}")
            thread = Thread(target=test_thread, args=(thread_id, return_values[thread_id]))
            threads.append(thread)

        # start_mutex.acquire()
        for t in threads:
            t.start()

        # start threads
        # start_mutex.release()

        print(f"parallelism={parallelism} waiting")

        # wait
        for t in threads:
            t.join()

        # do the average
        time_sum = 0.0
        for res in return_values:
            time_sum += res.value
        avg_time = time_sum / len(return_values)

        results[parallelism].append(avg_time)

        print(f"parallelism={parallelism} end: avg={avg_time:.2f}")

# print results
for parallelism in range(1, N_PARALLELISM_TO + 1):
    print(results[parallelism])

times_x = []
times_low = []
times_m = []
times_high = []

# calculate intervals
for i in range(1, N_PARALLELISM_TO + 1):
    arr = np.array(results[i])
    n = len(arr)
    m = arr.mean()
    s = arr.std()
    dof = n - 1
    confidence = 0.95

    t_crit = np.abs(t_student.ppf((1 - confidence) / 2, dof))

    low_value = m - s * t_crit / np.sqrt(n)
    high_value = m + s * t_crit / np.sqrt(n)

    times_low.append(m - low_value)
    times_m.append(m)
    times_high.append(high_value - m)
    times_x.append(i)

PlotUtils.use_tex()
plt.errorbar(times_x, times_m, yerr=[times_low, times_high], marker="x", markersize=3.0, markeredgewidth=1,
             linewidth=0.7, elinewidth=1, capsize=3)
plt.grid(color='#cacaca', linestyle='--', linewidth=0.5)

plt.xlabel("Parallelism")
plt.ylabel("Time (s)")

plt.savefig(f"./plot/test_parallelism_{Utils.current_time_string()}.pdf")
