from scatter.brew.core import make_callable
from concurrent.futures import ThreadPoolExecutor
from random import randint


NUMS = 1000


if __name__ == "__main__":
    # @scatter
    # def add(a: int, b: int) -> int:
    #     return a + b

    callable_func = make_callable("add")

    with ThreadPoolExecutor() as executor:
        res = executor.map(
            callable_func, [randint(0, 100) for _ in range(NUMS)], [randint(0, 100) for _ in range(NUMS)]
        )

    print(len(list(res)))
