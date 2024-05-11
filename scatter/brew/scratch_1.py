from scatter.brew.core import scatter


if __name__ == '__main__':
    @scatter
    def my_func(a: int, b: int) -> int:
        return a + b
