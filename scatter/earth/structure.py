import msgspec
from typing import Callable


class Function(msgspec.Struct):
    name: str
    version: int
    callable_: Callable
