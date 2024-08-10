# import inspect
from jurigged import make_recoder
from time import perf_counter
import cloudpickle

NUM = 10_00_000

# def sample(i, j=5, k=2):
#     return (i + j) * k


# new_source = inspect.getsource(sample)
# print(new_source)
new_source = """
def sample(i, j=5, k=2):
    return (i + j) * k
"""


def sample(i: int, j: float = 5.0) -> list[float]:
    return i + j


dumped_func = cloudpickle.dumps(sample)


print("Res:", sample(42, 42))

start = perf_counter()
for _ in range(NUM):
    sample(42, 42)
print("Normal call:", perf_counter() - start)


start = perf_counter()
for _ in range(NUM):
    cloudpickle.loads(dumped_func)(42, 42)
print("Cloudpickle call:", perf_counter() - start)


# Jurigged

recoder = make_recoder(sample)
recoder.patch(new_source)
recoder.patch_module
print("Res 2:", sample(42, 42))

start = perf_counter()
for _ in range(NUM):
    sample(42, 42)
print("Normal call:", perf_counter() - start)
