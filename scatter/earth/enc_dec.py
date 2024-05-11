import msgspec
import cloudpickle as pickle
from typing import Callable
from scatter.earth.structure import Function


def serialize_function(func: Callable) -> bytes:
    return pickle.dumps(func)


def deserialize_function(type: Callable, obj: bytes) -> Callable:
    return pickle.loads(obj)


encoder = msgspec.msgpack.Encoder(enc_hook=serialize_function)
decoder = msgspec.msgpack.Decoder(type=Function, dec_hook=deserialize_function)