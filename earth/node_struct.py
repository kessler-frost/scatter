import msgspec
from typing import Callable


class Node(msgspec.Struct):
    node_key: str
    node_func: Callable
