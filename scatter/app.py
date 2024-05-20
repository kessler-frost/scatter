from fastapi import FastAPI
from pydantic import BaseModel
import cloudpickle as pickle
from typing import Callable
from functools import wraps
from scatter.hash_model import Function


class Nums(BaseModel):
    a: int
    b: int


def ember(func_: Callable):

    try:

        # Unpickling once to attach all the wrappable things using `wraps`
        callable_func = pickle.loads(bytes.fromhex(Function.get(func_.__name__).callable_))

    except Exception:

        print("##################### NOT FOUND!!! ##########################")

        # Pickling the function for the first time
        Function(name=func_.__name__, callable_=pickle.dumps(func_).hex()).save()
        callable_func = func_

    @wraps(callable_func)
    def decorator(*args, **kwargs):

        # Unpickling the second time to run the function
        callable_func = pickle.loads(bytes.fromhex(Function.get(func_.__name__).callable_))

        return callable_func(*args, **kwargs)
    return decorator


app = FastAPI()


@app.put("/ember")
def put_ember(func_to_save: Function):
    func_to_save.save()


@app.get("/add")
@ember
def add(a: int, b: int) -> int:
    return a + b
