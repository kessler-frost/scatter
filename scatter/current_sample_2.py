import time
from scatter.main import sync, setup


def sample_3(i, j):
    return i * j


def sample_4(i, j):
    return i / j


sample_1 = setup("sample_1")

for i in range(1000):
    print(sample_1(100, 2))
    time.sleep(2)
    if i % 3 == 0:
        sample_1 = sync(sample_1)
