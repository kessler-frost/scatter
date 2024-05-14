from scatter.earth.cache_init import redis_client
from scatter.earth.encoder_decoder import deserialize_any
from typing import Dict, Any


# TODO: Use redis_client's pipeline for performance improvement when doing multiple operations


# ------------------- Callable storage -------------------

def store_callable(func_name: str, func_bytes: bytes) -> None:
    redis_client.set(f"callable@{func_name}", func_bytes)


def retrieve_callable(func_name: str) -> bytes:
    return redis_client.get(f"callable@{func_name}")


def delete_callable(func_name: str) -> None:
    redis_client.delete(f"callable@{func_name}")


# ------------------- Type hint storage -------------------

def store_type_hints(func_name: str, type_hint_bytes: bytes) -> None:
    redis_client.set(f"type_hints@{func_name}", type_hint_bytes)


def retrieve_type_hints(func_name: str) -> bytes:
    return redis_client.get(f"type_hints@{func_name}")


def delete_type_hints(func_name: str) -> None:
    redis_client.delete(f"type_hints@{func_name}")


# ------------------- Function params storage -------------------

def store_params(message_id: str, encoded_params: bytes) -> None:
    redis_client.set(f"params@{message_id}", encoded_params)


def retrieve_params(message_id: str) -> bytes:
    return redis_client.get(f"params@{message_id}")


def delete_params(message_id: str) -> None:
    redis_client.delete(f"params@{message_id}")
