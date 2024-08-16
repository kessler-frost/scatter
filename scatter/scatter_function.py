from typing import Any, Callable, Union, Optional
import cloudpickle
import redis
from functools import update_wrapper
from scatter.scratch_utils import FUNC_VERSIONS_HASH
import inspect


class ScatterFunction:
    
    def __init__(self, redis_client: Optional[redis.Redis] = None, name: Optional[str] = None, func: Optional[Callable] = None) -> None:
        self.r = redis_client or redis.Redis(protocol=3)
        self.pipe = self.r.pipeline()

        if not func and not name:
            raise ValueError("Either `name` or `func` is required to be passed")

        self.name = name
        self.func = func
        self._source = None
    
        if self.func:
            # Update the name to function's name irrespective of the passed in name
            self.name = func.__name__
            self._source = inspect.getsource(func)

        self._loaded_version = None

    @property
    def source(self):
        return self._source

    @property
    def loaded_version(self):
        return self._loaded_version
    
    def latest_version(self, raw: bool = False) -> Union[int, str, None]:
        raw_version = self.r.hget(FUNC_VERSIONS_HASH, self.name)
        return raw_version if raw else int(raw_version)

    def push(self) -> None:

        latest_version: Union[str, None] = self.latest_version(raw=True)
        ser_func: bytes = cloudpickle.dumps(self.func)

        # If a function already exists, save it in a new hash
        if latest_version is not None:
            current_mapping = self.r.hgetall(self.name)
            self.pipe.hset(
                f"{self.name}:{int(latest_version)}",
                mapping=current_mapping
            )

        # Save the function's updated pickle
        self.pipe.hset(
            self.name,
            mapping={
                "ser_func": ser_func,
                "source": self.source
            }
        )

        new_version = int(latest_version or -1) + 1

        self.pipe.hset(FUNC_VERSIONS_HASH, self.name, new_version)
        self.pipe.execute()

        self._loaded_version = new_version

    def pull(self, version: Optional[int] = None) -> None:

        latest_version = self.latest_version()
        if (
            version is None or 
            version >= latest_version or  # In case version is some high number
            latest_version == 0  # In case there doesn't exist any other version, thus no `{name}:{version}` hash exists
        ):
            mapping = self.r.hgetall(self.name)
            version = latest_version
        else:
            version = max(0, version)  # Ignore negative values
            mapping = self.r.hgetall(
                f"{self.name}:{version}",
            )
        
        ser_func, source = mapping.values()

        self._loaded_version = version
        self._source = source
        self.func = cloudpickle.loads(ser_func)

        # Update the "look" of the instance
        update_wrapper(self, self.func)
    
    def upgrade(self) -> None:
        self.pull(self.loaded_version + 1)
    
    def downgrade(self) -> None:
        self.pull(self.loaded_version - 1)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.func(*args, **kwargs)
