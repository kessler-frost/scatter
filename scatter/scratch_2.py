from scatter.brew import assemble, show_versions

# def my_func(a: int, b: int) -> int:
#     return a + b


if __name__ == '__main__':
    print(show_versions())

    my_func = assemble("my_func")

    res = []
    for i in range(10):
        res.append(my_func(i * 2, i))

    # vaporize("my_func")
