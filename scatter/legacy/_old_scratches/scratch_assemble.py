from scatter.brew.core import make_callable

if __name__ == '__main__':

    while True:
        for i in range(10):
            my_func = make_callable(f"my_func_{i}")
            print(my_func(i, i * 2))

        break
