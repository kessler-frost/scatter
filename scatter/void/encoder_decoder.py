import msgspec
from typing import Any, Type
import cloudpickle as pickle


def serialize_any(obj: Any) -> bytes:
    return pickle.dumps(obj)


encoder = msgspec.msgpack.Encoder(enc_hook=serialize_any)


def deserialize_any(type_: Type, obj: bytes) -> Any:
    return pickle.loads(obj)


def get_decoder(struct_type: msgspec.Struct) -> msgspec.msgpack.Decoder:
    return msgspec.msgpack.Decoder(type=struct_type, dec_hook=deserialize_any)
