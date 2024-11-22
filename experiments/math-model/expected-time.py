import numpy as np
from sklearn import preprocessing
import getopt
import sys


def computeTime(k, mi, values):
    out = 0.0
    out += (k+1)*mi
    for value in values:
        out -= value
    return out


def generateArrivalTimes(from_t, to_t, k):
    def generateUniform():
        return np.random.uniform(from_t, to_t, k)

    def generatePoisson():
        v = np.random.exponential(1 / k, size=k)
        res = []
        summation = 0.0
        for val in v:
            summation += val
            res.append(summation)
        #v_r = v.reshape(1, -1)
        #v_n = preprocessing.normalize(v_r, norm='l1')
        return res

    return generatePoisson()


def startTest(k, mi, runs, d):
    print("\n[SIMULATION] Starting test with k = %d, mi = %.2f" % (k, mi))
    times = 0.0

    print("[SIMULATION] Try %d/%d Time %.2f" % (0, runs, 0.0), end="")
    for i in range(runs):
        values = generateArrivalTimes(0.0, mi, k)
        #print("Generated " + str(values))
        time = computeTime(k, mi, values)
        times += time
        print("\r[SIMULATION] Try %d/%d Time %.2f" % (i + 1, runs, time), end="")

    mean = times/float(runs)
    print("\n[SIMULATION] End with mean time %.2f" % mean)
    return mean


def startSuite(from_k, to_k, mi, runs, d):
    times = []
    print("[TEST] Starting test suite from k = %d to k = %d" % (from_k, to_k))
    for i in range(from_k, to_k + 1):
        times.append(startTest(i, mi, runs, d))

    plotResults(times)


def plotResults(times):
    print("\n[RESULTS]")
    for value in times:
        value_s = str(value).replace(".", ",")
        print(value_s)


def main(argv):
    print("===== Expected time test suite =====")
    from_k = 1
    to_k = 10
    mi = -1.0
    d = 0
    runs = 100

    usage = "expected-time.py"
    try:
        opts, args = getopt.getopt(
            argv, "hm:d:r:", ["from-k=", "to-k="])
    except getopt.GetoptError:
        print(usage)
        sys.exit(2)
    for opt, arg in opts:
        #print(opt + " -> " + arg)
        if opt == '-h':
            print(usage)
            sys.exit()
        elif opt in ("-m"):
            mi = float(arg)
        elif opt in ("-d"):
            d = 0
        elif opt in ("-r"):
            runs = int(arg)
        elif opt in ("--from-k"):
            from_k = int(arg)
        elif opt in ("--to-k"):
            to_k = int(arg)

    if mi < 0:
        print("Some needed parameter was not given")
        print(usage)
        sys.exit()

    startSuite(from_k, to_k, mi, runs, d)


if __name__ == "__main__":
    main(sys.argv[1:])
