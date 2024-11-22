import numpy as np
from sklearn import preprocessing
import matplotlib.pyplot as plt

k = 10
mi = 1

summations = []
values_total = []

for i in range(100000):
    values = np.random.exponential(1/10, size=10)
    res = []
    summation = 0.0
    for val in values:
        summation += val
        res.append(summation)

    summations.append(summation)
    for v in res:
        values_total.append(v)


count, bins, ignored = plt.hist(values, 14, density=True)
plt.show()
