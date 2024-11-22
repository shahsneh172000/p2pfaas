def computePb(l, mi, k):
    ro = float(l)/float(mi)
    return ((1-ro)*pow(ro, k))/(1-pow(ro, k+1))


def delay(l, mi, k):
    ro = float(l)/float(mi)
    pb = computePb(l, mi, k)

    total = 0.0
    for i in range(1, k + 1):
        total += i*pow(ro, i)

    return (((1-ro)/(1-pow(ro, k+1)))*total)/(float(l)*(1-pb))


K = 10
mi = 1 / 0.3
l = 1.0

while True:
    print("%.2f %.6f %.6f" % (l, computePb(l, mi, K), delay(l, mi, K)))
    l += 0.1

    if l > 10.0:
        break
