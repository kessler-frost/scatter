from diskcache import FanoutCache
from pathlib import Path
from typing import Callable
from scatter.earth.encoder_decoder import deserialize_any
import os


cache_dir = str(Path(__file__).parent / "disk_cache")

cache = FanoutCache(cache_dir, shards=os.cpu_count())


# ------------------- Callable storage -------------------

def store_callable(func_name: str, func_bytes: bytes) -> None:
    cache.set(f"callable@{func_name}", func_bytes)


def retrieve_callable(func_name: str) -> bytes:
    return cache.get(f"callable@{func_name}")


def delete_callable(func_name: str) -> None:
    cache.delete(f"callable@{func_name}")


# ------------------- Type hint storage -------------------

def store_type_hints(func_name: str, type_hint_bytes: bytes) -> None:
    cache.set(f"type_hints@{func_name}", type_hint_bytes)


def retrieve_type_hints(func_name: str) -> bytes:
    return cache.get(f"type_hints@{func_name}")


def delete_type_hints(func_name: str) -> None:
    cache.delete(f"type_hints@{func_name}")


# ------------------- Function params storage -------------------

def store_params(message_id: str, encoded_params: bytes) -> None:
    cache.set(f"params@{message_id}", encoded_params)


def retrieve_params(message_id: str) -> bytes:
    return cache.get(f"params@{message_id}")


def delete_params(message_id: str) -> None:
    cache.delete(f"params@{message_id}")


# ------------------- Python object retrieval with cache -------------------

def get_callable_function(func_name: str) -> Callable:
    func_bytes = retrieve_callable(func_name)
    return deserialize_any(None, func_bytes)


def get_type_hints(func_name: str) -> dict:
    type_hint_bytes = retrieve_type_hints(func_name)
    return deserialize_any(None, type_hint_bytes)
