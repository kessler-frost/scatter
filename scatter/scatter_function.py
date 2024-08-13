from typing import Any, Callable, Union, Optional
import cloudpickle
import redis
from functools import update_wrapper


FUNC_VERSIONS_HASH = "func_versions_hash"


class ScatterFunction:
    
    def __init__(self, redis_client: redis.Redis, func: Optional[Callable] = None, name: Optional[str] = None) -> None:
        self.r = redis_client
        self.pipe = self.r.pipeline()

        if not func and not name:
            raise ValueError("Either `name` or `func` is required to be passed")

        self.func = func
        self.name = name
    
        if self.func:
            # Update the name to function's name irrespective of the passed in name
            self.name = self.func.__name__

        self._loaded_version = None

    @property
    def loaded_version(self):
        return self._loaded_version
    

    def push(self) -> None:
        name: str = self.func.__name__

        latest_version: Union[str, None] = self.latest_version(raw=True)
        ser_func: bytes = cloudpickle.dumps(self.func)

        # If a function already exists, save it in a new hash
        if latest_version is not None:
            current_mapping = self.r.hgetall(name)
            self.pipe.hset(
                f"{name}:{int(latest_version)}",
                mapping=current_mapping
            )

        # Save the function's updated pickle
        self.pipe.hset(
            name,
            mapping={
                "ser_func": ser_func
            }
        )

        new_version = int(latest_version or -1) + 1

        self.pipe.hset(FUNC_VERSIONS_HASH, name, new_version)
        self.pipe.execute()

        self._loaded_version = new_version

    def pull(self, version: Optional[int] = None) -> None:

        latest_version = self.latest_version()
        if (
            version is None or 
            version >= latest_version or  # In case version is some high number
            latest_version == 0  # In case there doesn't exist any other version, thus no `{name}:{version}` hash exists
        ):
            ser_func = self.r.hget(self.name, "ser_func")
            version = latest_version
        else:
            version = max(0, version)
            ser_func = self.r.hget(
                f"{self.name}:{version}",
                "ser_func"
            )

        self._loaded_version = version
        self.func = cloudpickle.loads(ser_func)

        # Update the "look" of the instance
        update_wrapper(self, self.func)

    def latest_version(self, raw: bool = False) -> Union[int, str, None]:
        raw_version = self.r.hget(FUNC_VERSIONS_HASH, self.name)
        return raw_version if raw else int(raw_version)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.func(*args, **kwargs)
