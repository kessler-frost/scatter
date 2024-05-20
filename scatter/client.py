import requests
from pydantic import BaseModel


class MyNums(BaseModel):
    a: int
    b: int


if __name__ == "__main__":

    nums = MyNums(a=1, b=2)

    response = requests.get(
        "http://127.0.0.1:8000/add", json=nums.model_dump()
    )

    print(response.json())
