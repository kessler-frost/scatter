from scatter.brew.core import scatter, make_callable


if __name__ == "__main__":
    @scatter
    def add(a: int, b: int) -> int:
        return a + b

    print(make_callable("add")(1, 2))
