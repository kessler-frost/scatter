import os
from pathlib import Path
from typing import Callable

import redis
from diskcache import FanoutCache

from scatter.earth.encoder_decoder import deserialize_any
from scatter.ember.constants import REDIS_DB, REDIS_HOST, REDIS_PORT


class Storage:
    def __init__(self, backend: str = "diskcache", backend_kwargs: dict = None):

        if backend_kwargs is None:
            backend_kwargs = {}

        self.backend = backend

        if self.backend == "redis":

            default_backend_kwargs = {
                "host": REDIS_HOST,
                "port": REDIS_PORT,
                "db": REDIS_DB,
            }

            backend_kwargs = {**default_backend_kwargs, **backend_kwargs}

            # TODO: Can use redis_client's pipeline for performance improvement when doing multiple operations
            self.cache = redis.StrictRedis(**backend_kwargs)

        elif self.backend == "diskcache":
            directory = str(Path(__file__).parent / "disk_cache")

            default_backend_kwargs = {
                "directory": directory,
                "shards": os.cpu_count(),
            }

            backend_kwargs = {**default_backend_kwargs, **backend_kwargs}

            self.cache = FanoutCache(**backend_kwargs)
        else:
            raise ValueError(f"Invalid backend: {self.backend}")

    def store_callable(self, func_name: str, func_bytes: bytes) -> None:
        self.cache.set(f"callable@{func_name}", func_bytes)

    def retrieve_callable(self, func_name: str) -> bytes:
        return self.cache.get(f"callable@{func_name}")

    def delete_callable(self, func_name: str) -> None:
        self.cache.delete(f"callable@{func_name}")

    def store_type_hints(self, func_name: str, type_hint_bytes: bytes) -> None:
        self.cache.set(f"type_hints@{func_name}", type_hint_bytes)

    def retrieve_type_hints(self, func_name: str) -> bytes:
        return self.cache.get(f"type_hints@{func_name}")

    def delete_type_hints(self, func_name: str) -> None:
        self.cache.delete(f"type_hints@{func_name}")

    def store_params(self, message_id: str, encoded_params: bytes) -> None:
        self.cache.set(f"params@{message_id}", encoded_params)

    def retrieve_params(self, message_id: str) -> bytes:
        return self.cache.get(f"params@{message_id}")

    def delete_params(self, message_id: str) -> None:
        self.cache.delete(f"params@{message_id}")

    def get_callable_function(self, func_name: str) -> Callable:
        func_bytes = self.retrieve_callable(func_name)
        return deserialize_any(None, func_bytes)

    def get_type_hints(self, func_name: str) -> dict:
        type_hint_bytes = self.retrieve_type_hints(func_name)
        return deserialize_any(None, type_hint_bytes)
