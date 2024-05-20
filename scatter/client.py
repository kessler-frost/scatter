import requests
from scatter.hash_model import Function
from typing import Callable
import cloudpickle as pickle


def serialize(func_: Callable) -> str:
    return pickle.dumps(func_).hex()


if __name__ == "__main__":

    URL = "http://127.0.0.1:8000"

    response = requests.get(
        f"{URL}/add", params={"a": 1, "b": 2}
    )

    print(response.text)

    def add(a: int, b: int) -> int:
        return 42

    response = requests.put(
        f"{URL}/ember", json=Function(name="add", callable_=serialize(add)).model_dump()
    )

    response = requests.get(
        f"{URL}/add", params={"a": 1, "b": 2}
    )

    print(response.text)

    response = requests.get(
        f"{URL}/add", params={"a": 1, "b": 2, "c": 3}
    )

    print(response.text)
