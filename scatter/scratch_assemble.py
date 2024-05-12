from scatter.brew.core import make_callable

# def my_func(a: int, b: int) -> int:
#     return a + b


if __name__ == '__main__':
    # print(show_versions())

    res = []
    for i in range(1):
        my_func = make_callable("my_func")
        res.append(my_func(i * 2, i))

    # vaporize("my_func")
