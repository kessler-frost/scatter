from scatter.brew.core import assemble, list_functions


# def my_func(a: int, b: int) -> int:
#     return a + b


if __name__ == '__main__':
    print(list_functions())

    my_func = assemble("my_func")

    res = []
    for i in range(100_000):
        res.append(my_func(i * 2, i))
