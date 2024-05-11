import msgspec
from typing import Callable


class Function(msgspec.Struct):
    name: str
    callable_: Callable
