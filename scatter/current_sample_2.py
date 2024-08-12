import time
from scatter.main import assemble, scatter


@scatter
def sample_3(i, j):
    return i * j


@scatter
def sample_4(i, j):
    return i / j


sample_1 = assemble("sample_1")
sample_2 = assemble("sample_2")

for i in range(100):
    print(sample_1(100, 2))
    print(sample_2(100, 2))
    time.sleep(2)
    if i % 3 == 0:
        sample_1.sync()
        sample_2.sync()
