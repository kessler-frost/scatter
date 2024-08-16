from scatter.scatter_function import ScatterFunction
from functools import wraps


def init():
    ...


def scatter(_func = None) -> ScatterFunction:
    scatter_obj = ScatterFunction(func=_func)
    return wraps(_func)(scatter_obj)


def assemble(name: str) -> ScatterFunction:
    scatter_obj = ScatterFunction(name=name)
    scatter_obj.pull()
    return scatter_obj
