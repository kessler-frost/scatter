from scatter import scatter
import random


if __name__ == '__main__':
    @scatter
    def my_func(a: int, b: int) -> int:
        return (a + b) * random.randint(1, 100)
