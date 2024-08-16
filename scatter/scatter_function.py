from typing import Any, Callable, Union, Optional
import cloudpickle
import redis
import redis.asyncio as aredis
from functools import update_wrapper
from scatter.scratch_utils import FUNC_VERSIONS_HASH, ASYNC_SLEEP_TIME
import inspect
import asyncio


class ScatterFunction:
    
    def __init__(self, redis_client: Optional[redis.Redis] = None, name: Optional[str] = None, func: Optional[Callable] = None) -> None:
        self.redis_client = redis_client
        self.pipe = self.redis_client.pipeline()

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
        raw_version = self.redis_client.hget(FUNC_VERSIONS_HASH, self.name)
        return raw_version if raw else int(raw_version)

    def push(self) -> None:

        latest_version: Union[str, None] = self.latest_version(raw=True)
        ser_func: bytes = cloudpickle.dumps(self.func)

        # If a function already exists, save it in a new hash
        if latest_version is not None:
            current_mapping = self.redis_client.hgetall(self.name)
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

        new_version = int(latest_version or 0) + 1

        self.pipe.hset(FUNC_VERSIONS_HASH, self.name, new_version)
        self.pipe.execute()

        self._loaded_version = new_version

    def pull(self, version: Optional[int] = None) -> None:

        latest_version = self.latest_version()
        if (
            version is None or 
            version >= latest_version or  # In case version is some high number
            latest_version == 1  # In case there doesn't exist any other version, thus no `{name}:{version}` hash exists
        ):
            # Get the latest version of the function
            mapping = self.redis_client.hgetall(self.name)
            version = latest_version
        else:
            version = max(1, version)  # Ignoring reserved and negative values
            mapping = self.redis_client.hgetall(
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


class AsyncScatterFunction:
    
    def __init__(self, redis_client: Optional[aredis.Redis], name: Optional[str] = None, func: Optional[Callable] = None) -> None:
        self.redis_client = redis_client
        self.pipe = self.redis_client.pipeline()
        self.pubsub = self.redis_client.pubsub(ignore_subscribe_messages=True)

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
    
    async def latest_version(self, raw: bool = False) -> Union[int, str, None]:
        raw_version = await self.redis_client.hget(FUNC_VERSIONS_HASH, self.name)
        return raw_version if raw else int(raw_version)

    async def push(self, update_existing: bool = True) -> None:

        latest_version: Union[str, None] = await self.latest_version(raw=True)
        ser_func: bytes = cloudpickle.dumps(self.func)

        # If a function already exists, save it in a new hash
        if latest_version is not None:
            current_mapping = await self.redis_client.hgetall(self.name)
            await self.pipe.hset(
                f"{self.name}:{int(latest_version)}",
                mapping=current_mapping
            )

        # Save the function's updated pickle
        await self.pipe.hset(
            self.name,
            mapping={
                "ser_func": ser_func,
                "source": self.source
            }
        )

        new_version = int(latest_version or 0) + 1

        await self.pipe.hset(FUNC_VERSIONS_HASH, self.name, new_version)
        if update_existing:
            await self.pipe.publish(f"channel:{self.name}", -1)
        await self.pipe.execute()

        self._loaded_version = new_version

    async def pull(self, version: Optional[int] = None) -> None:

        latest_version = await self.latest_version()
        if (
            version is None or 
            version >= latest_version or  # In case version is some high number
            latest_version == 1  # In case there doesn't exist any other version, thus no `{name}:{version}` hash exists
        ):
            mapping = await self.redis_client.hgetall(self.name)
            version = latest_version
        else:
            version = max(1, version)  # Ignore negative values
            mapping = await self.redis_client.hgetall(
                f"{self.name}:{version}",
            )

        ser_func, source = mapping.values()

        self._loaded_version = version
        self._source = source
        self.func = cloudpickle.loads(ser_func)

        # Update the "look" of the instance
        update_wrapper(self, self.func)
    
    async def upgrade(self) -> None:
        await self.pull(self.loaded_version + 1)
    
    async def downgrade(self) -> None:
        await self.pull(self.loaded_version - 1)

    async def update_all(self, version: Optional[int] = None) -> None:
        await self.redis_client.publish(f"channel:{self.name}", max(-1, version))

    async def schedule(self) -> None:
        await self.pubsub.subscribe(f"channel:{self.name}")
        print("Subscribed!")

        while True:
            message = await self.pubsub.get_message()
            if message is not None:
                print("Got a message", message)
                to_version = int(message["data"].decode())
                if to_version != self.loaded_version:
                    await self.pull(to_version)
                elif to_version == -1:  # -1 will lead to updating to the latest version
                    await self.pull()
                
            await asyncio.sleep(ASYNC_SLEEP_TIME)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.func(*args, **kwargs)
