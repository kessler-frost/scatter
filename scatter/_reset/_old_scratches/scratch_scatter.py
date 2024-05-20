from scatter.brew.core import scatter
import random


if __name__ == '__main__':
    for i in range(100_000):
        def my_func(a: int, b: int) -> int:
            return (a + b) * random.randint(1, 100)

        my_func.__name__ = f"my_func_{i}"
        scatter(my_func)
