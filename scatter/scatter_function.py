from typing import Any, Callable, Union
import cloudpickle
import redis
from functools import update_wrapper


FUNC_VERSIONS_HASH = "func_versions_hash"


class ScatterFunction:
    
    def __init__(self, redis_client: redis.Redis, func: Callable = None, name: str = None) -> None:
        self.r = redis_client
        self.pipe = self.r.pipeline()
        
        if not func and not name:
            raise ValueError("Either `name` or `func` is required to be passed")

        self.func = func
        self.name = name
    
        if self.func:
            # Update the name to function's name irrespective of the passed in name
            self.name = self.func.__name__

    def save(self) -> None:
        name: str = self.func.__name__

        current_version: Union[str, None] = self.r.hget(FUNC_VERSIONS_HASH, name)
        ser_func: bytes = cloudpickle.dumps(self.func)

        # If a function already exists, save it in a new hash
        if current_version is not None:
            current_mapping = self.r.hgetall(name)
            self.pipe.hset(
                f"{name}:{int(current_version)}",
                mapping=current_mapping
            )

        # Save the function's updated pickle
        self.pipe.hset(
            name,
            mapping={
                "ser_func": ser_func
            }
        )

        self.pipe.hset(FUNC_VERSIONS_HASH, name, int(current_version or -1) + 1)
        self.pipe.execute()

    def sync(self) -> None:
        ser_func = self.r.hget(self.name, "ser_func")
        self.func = cloudpickle.loads(ser_func)
        
        # Update the "look" of the instance
        update_wrapper(self, self.func)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.func(*args, **kwargs)
