def Delay(l, K):
    norm = 0
    for k in range(0, K+1):
        norm += pow(l, k)
    #norm = (1-l)/(1-pow(l,K+1))
    norm = 1/norm
    tot = 0
    delay = 0
    pb = norm*pow(l, K)
    # print 'norm',norm
    for k in range(1, K+1):
        pi = norm*pow(l, k)
        # print k,pi
        delay += (k)*pi
        tot += pi
    # return tot
    return delay/(l*(1-pb))


K = 10
for load in range(1, 10*K):
    l = (0.0+load)/K
    print(l, Delay(l, K)*3/10.0)
