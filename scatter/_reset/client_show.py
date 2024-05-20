from scatter.brew.core import make_callable, current_version, rollback, scatter


if __name__ == "__main__":

    num_1 = 42
    num_2 = 42 * 24

    @scatter
    def add(a: int, b: int) -> int:
        return a + b

    # @scatter
    # def add(a: int, b: int, c: int) -> int:
    #     return a + b + c

    print("Current function version:", current_version("add"))

    callable_func = make_callable("add")

    print("Function call result:", callable_func(num_1, num_2))

    print("Current function version:", current_version("add"))

    # Rollback the function
    rollback("add")
    print("Version after rollback:", current_version("add"))

    # Calling rolledback function
    callable_func = make_callable("add")
    print("Rolled back function call result:", callable_func(num_1, num_2))
