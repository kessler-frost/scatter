# from scatter.models import FunctionModel
from redis_om import Migrator
from typing import Callable
import cloudpickle
import inspect


def save(function_: Callable, name: str = None) -> None:
    ...


def make_callable(name: str) -> Callable:
    ...
