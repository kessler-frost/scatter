from scatter.brew.core import make_callable, scatter, current_version, vaporize, rollback
from concurrent.futures import ThreadPoolExecutor
from random import randint


NUMS = 100


if __name__ == "__main__":

    @scatter
    def add(a: int, b: int) -> int:
        return a + b

    # @scatter
    # def add(a: int, b: int, c: int) -> int:
    #     return a + b + c

    num_1 = randint(0, 100)
    num_2 = randint(0, 100)

    callable_func = make_callable("add")

    print(callable_func(num_1, num_2))

    print("Current version:", current_version("add"))

    # Rollback the function
    # rollback("add")

    # print("Version after rollback:", current_version("add"))

    # Delete the function
    print("Deleting the function...")
    # vaporize("add")

    # with ThreadPoolExecutor() as executor:
    #     res = executor.map(
    #         callable_func, [randint(0, 100) for _ in range(NUMS)], [randint(0, 100) for _ in range(NUMS)]
    #     )

    # print(len(list(res)))
