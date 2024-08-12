import time
from scatter.main import sync
import inspect


def sample_3(i, j):
    return i * j


def sample_4(i, j):
    return i / j


sample_1 = sync("sample_1")

while(True):
    print(sample_1(100, 2))
    time.sleep(2)
    sample_1 = sync("sample_1")
