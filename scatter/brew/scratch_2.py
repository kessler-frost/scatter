from scatter.brew.core import assemble


# def my_func(a: int, b: int) -> int:
#     return a + b


if __name__ == '__main__':
    my_func = assemble("my_func")

    res = []
    for i in range(100_000):
        res.append(my_func(i * 2, i))

    # print(res[:10])
