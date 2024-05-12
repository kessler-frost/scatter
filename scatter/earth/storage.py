import typing

import cloudpickle as pickle
import msgspec

from scatter.earth.cache import cache, index
from scatter.earth.key_helpers import (func_name_to_callable_key,
                                       func_name_to_struct_key)

# -------------------------- Encoder / Decoder --------------------------


def encode(obj: typing.Union[msgspec.Struct, typing.Callable, msgspec.inspect.CustomType]) -> bytes:
    return pickle.dumps(obj)


def decode(obj: bytes) -> typing.Union[msgspec.Struct, typing.Callable, msgspec.inspect.CustomType]:
    return pickle.loads(obj)


msgspec_encoder = msgspec.msgpack.Encoder(enc_hook=encode)

# Dynamically create the decoder since it requires the dynamically created msgspec.Struct class


# -------------------------- Storage / Retrieval --------------------------

def store(encoded_struct: bytes, encoded_callable: bytes, func_name: str):

    # Get the version of the function from the index
    new_version = index.get(func_name, 0) + 1

    # Store the encoded function struct in the cache
    struct_key = func_name_to_struct_key(func_name, new_version)
    cache[struct_key] = encoded_struct

    # Store the callable in the cache
    callable_key = func_name_to_callable_key(func_name, new_version)
    cache[callable_key] = encoded_callable

    # Update the index with the new version
    index[func_name] = new_version

    # Print the version and index items
    print(f"Version: {new_version} of {func_name} stored.")
    print(f"Index: {dict(index.items())}")


def show_versions() -> dict:
    return dict(index.items())


def retrieve_struct(func_name: str) -> bytes:
    version = index[func_name]
    struct_key = func_name_to_struct_key(func_name, version)

    # Return the encoded struct from the cache
    return cache[struct_key]


def retrieve_callable(func_name: str) -> bytes:
    """
    To be used inside a worker to retrieve the encoded callable from the cache.
    """

    version = index[func_name]
    callable_key = func_name_to_callable_key(func_name, version)

    # Return the encoded callable from the cache
    return cache[callable_key]


# -------------------------- Deletion / Rollback --------------------------

def delete(func_name: str):
    version = index[func_name]

    for i in range(1, version + 1):
        del cache[func_name_to_struct_key(func_name, i)]
        del cache[func_name_to_callable_key(func_name, i)]
    del index[func_name]


def rollback(func_name: str):
    version = index[func_name]

    if version > 1:
        index[func_name] = version - 1
        del cache[func_name_to_struct_key(func_name, version)]


def clear_cache():
    cache.clear()
    index.clear()
