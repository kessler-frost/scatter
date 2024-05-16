from scatter.brew.core import make_callable, scatter, current_version, vaporize, rollback
from random import randint


if __name__ == "__main__":

    num_1 = randint(0, 100)
    num_2 = randint(0, 100)

    @scatter
    def add(a: int, b: int) -> int:
        return a + b

    # @scatter
    # def add(a: int, b: int, c: int) -> int:
    #     return a + b + c

    callable_func = make_callable("add")

    print(callable_func(num_1, num_2))

    print("Current version:", current_version("add"))

    # # Rollback the function
    # rollback("add")

    # print("Version after rollback:", current_version("add"))

    # # Delete the function
    # print("Deleting the function...")
    # vaporize("add")
