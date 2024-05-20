from fastapi import FastAPI
from pydantic import BaseModel


class Nums(BaseModel):
    a: int
    b: int


app = FastAPI()


@app.get("/add")
def add(nums: Nums) -> int:
    return nums.a + nums.b
