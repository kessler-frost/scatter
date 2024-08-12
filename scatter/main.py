import redis
from scatter.scatter_function import ScatterFunction
from functools import wraps

r = redis.Redis()


def scatter(_func = None) -> ScatterFunction:
    scatter_obj = ScatterFunction(r, _func)
    return wraps(_func)(scatter_obj)


def assemble(name: str) -> ScatterFunction:
    scatter_obj = ScatterFunction(r, name=name)
    scatter_obj.pull()
    return scatter_obj
