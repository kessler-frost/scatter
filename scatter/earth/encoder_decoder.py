import msgspec
from typing import Any, Type
import cloudpickle as pickle


def serialize_any(obj: Any) -> bytes:
    return pickle.dumps(obj)


def deserialize_any(type_: Type, obj: bytes) -> Any:
    return pickle.loads(obj)


encoder = msgspec.msgpack.Encoder(enc_hook=serialize_any)


def generate_decoder(struct_type: msgspec.Struct.__class__) -> msgspec.msgpack.Decoder:
    return msgspec.msgpack.Decoder(type=struct_type, dec_hook=deserialize_any)
