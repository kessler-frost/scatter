from scatter.brew.core import scatter


if __name__ == "__main__":

    @scatter
    def add(a: str, b: str, c: str, d: str) -> str:
        return a + b + c + d
