import redis
from scatter.constants import REDIS_HOST, REDIS_PORT, REDIS_DB
from typing import Tuple

redis_store = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)


# ------------------- Callable storage -------------------

def store_callable(func_name: str, func_bytes: bytes) -> None:
    redis_store.set(f"callable@{func_name}", func_bytes)


def retrieve_callable(func_name: str) -> bytes:
    return redis_store.get(f"callable@{func_name}")


def delete_callable(func_name: str) -> None:
    redis_store.delete(f"callable@{func_name}")


# ------------------- Type hint storage -------------------

def store_type_hints(func_name: str, type_hint_bytes: bytes) -> None:
    redis_store.set(f"type_hints@{func_name}", type_hint_bytes)


def retrieve_type_hints(func_name: str) -> bytes:
    return redis_store.get(f"type_hints@{func_name}")


def delete_type_hints(func_name: str) -> None:
    redis_store.delete(f"type_hints@{func_name}")


# ------------------- Function args/kwargs storage -------------------

def store_params(message_id: str, args_bytes: bytes, kwargs_bytes: bytes) -> None:
    redis_store.set(f"args@{message_id}", args_bytes)
    redis_store.set(f"kwargs@{message_id}", kwargs_bytes)


def retrieve_params(message_id: str) -> Tuple[bytes, bytes]:
    return redis_store.get(f"args@{message_id}"), redis_store.get(f"kwargs@{message_id}")


def delete_params(message_id: str) -> None:
    redis_store.delete(f"args@{message_id}")
    redis_store.delete(f"kwargs@{message_id}")
