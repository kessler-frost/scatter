from scatter.brew.core import make_callable


if __name__ == '__main__':

    res = []
    for i in range(1):
        my_func = make_callable(f"my_func_{i}")
        res.append(my_func(42, 24))
