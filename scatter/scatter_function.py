from typing import Any, Callable, Union, Optional
import cloudpickle
from functools import update_wrapper
from scatter.utils import ASYNC_SLEEP_TIME, RESERVED_VERSIONS, safe_decode, dict_decode
from scatter.state_manager import state_manager
import inspect
import asyncio


class ScatterFunction:
    def __init__(
        self, name: Optional[str] = None, func: Optional[Callable] = None
    ) -> None:
        self.redis_client = state_manager.redis_client
        self.pipe = self.redis_client.pipeline()

        self.aredis_client = state_manager.aredis_client
        self.apipe = self.aredis_client.pipeline()

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

    def is_runnable(self):
        return self.func is not None

    def latest_version(self, raw: bool = False) -> Union[int, str, None]:
        raw_version = safe_decode(
            self.redis_client.hget(state_manager.FUNC_VERSIONS_HASH_NAME, self.name)
        )
        return raw_version if raw else int(raw_version)

    async def alatest_version(self, raw: bool = False) -> Union[int, str, None]:
        raw_version = safe_decode(
            await self.aredis_client.hget(
                state_manager.FUNC_VERSIONS_HASH_NAME, self.name
            )
        )
        return raw_version if raw else int(raw_version)

    def push(self, update_existing: bool = True) -> None:
        latest_version: Union[str, None] = self.latest_version(raw=True)
        ser_func: bytes = cloudpickle.dumps(self.func)

        # If a function already exists, save it in a new hash
        if latest_version is not None:
            current_mapping = dict_decode(
                self.redis_client.hgetall(f"{state_manager.ROOT_PREFIX}:{self.name}")
            )
            self.pipe.hset(
                f"{state_manager.ROOT_PREFIX}:{self.name}:{int(latest_version)}",
                mapping=current_mapping,
            )

        # Save the function's updated pickle
        self.pipe.hset(
            f"{state_manager.ROOT_PREFIX}:{self.name}",
            mapping={"ser_func": ser_func, "source": self.source},
        )

        new_version = int(latest_version or 0) + 1

        self.pipe.hset(state_manager.FUNC_VERSIONS_HASH_NAME, self.name, new_version)
        if update_existing:
            self.pipe.publish(f"{state_manager.CHANNEL_NAME}:{self.name}", RESERVED_VERSIONS.LATEST)
        self.pipe.execute()

        self._loaded_version = new_version

    async def apush(self, update_existing: bool = True) -> None:
        latest_version: Union[str, None] = await self.alatest_version(raw=True)
        ser_func: bytes = cloudpickle.dumps(self.func)

        # If a function already exists, save it in a new hash
        if latest_version is not None:
            current_mapping = dict_decode(
                await self.aredis_client.hgetall(
                    f"{state_manager.ROOT_PREFIX}:{self.name}"
                )
            )
            await self.apipe.hset(
                f"{state_manager.ROOT_PREFIX}:{self.name}:{int(latest_version)}",
                mapping=current_mapping,
            )

        # Save the function's updated pickle
        await self.apipe.hset(
            f"{state_manager.ROOT_PREFIX}:{self.name}",
            mapping={"ser_func": ser_func, "source": self.source},
        )

        new_version = int(latest_version or 0) + 1

        await self.apipe.hset(
            state_manager.FUNC_VERSIONS_HASH_NAME, self.name, new_version
        )
        if update_existing:
            await self.apipe.publish(
                f"{state_manager.CHANNEL_NAME}:{self.name}", RESERVED_VERSIONS.LATEST
            )
        await self.apipe.execute()

        self._loaded_version = new_version

    def pull(self, version: Optional[int] = None) -> None:
        if version == RESERVED_VERSIONS.NO_CHANGE:
            return

        latest_version = self.latest_version(raw=True)
        if latest_version is None:
            raise KeyError(f"Function {self.name} doesn't exist")

        if (
            version is None
            or version == latest_version
            or latest_version
            == 1  # In case there doesn't exist any other version, thus no `{name}:{version}` hash exists
            or version == RESERVED_VERSIONS.LATEST
        ):
            mapping = dict_decode(
                self.redis_client.hgetall(f"{state_manager.ROOT_PREFIX}:{self.name}")
            )
            version = latest_version
        else:
            if version > latest_version:
                version = min(latest_version, version)
            else:
                version = max(1, version)
            mapping = dict_decode(
                self.redis_client.hgetall(
                    f"{state_manager.ROOT_PREFIX}:{self.name}:{version}",
                )
            )

        self._loaded_version = version
        self._source = mapping["source"]
        self.func = cloudpickle.loads(mapping["ser_func"])

        # Update the "look" of the instance
        update_wrapper(self, self.func)

    async def apull(self, version: Optional[int] = None) -> None:
        if version == RESERVED_VERSIONS.NO_CHANGE:
            return

        latest_version = await self.alatest_version(raw=True)
        if latest_version is None:
            raise KeyError(f"Function {self.name} doesn't exist")

        if (
            version is None
            or version == latest_version
            or version == RESERVED_VERSIONS.LATEST
            # In case there doesn't exist any other version, thus no `{name}:{version}` hash exists
            or latest_version == 1
        ):
            mapping = dict_decode(
                await self.aredis_client.hgetall(
                    f"{state_manager.ROOT_PREFIX}:{self.name}"
                )
            )
            version = latest_version
        else:
            if version > latest_version:
                version = min(latest_version, version)
            else:
                version = max(1, version)
            mapping = dict_decode(
                await self.aredis_client.hgetall(
                    f"{state_manager.ROOT_PREFIX}:{self.name}:{version}",
                )
            )

        self._loaded_version = version
        self._source = mapping["source"]
        self.func = cloudpickle.loads(mapping["ser_func"])

        # Update the "look" of the instance
        update_wrapper(self, self.func)

    def upgrade(self) -> None:
        self.pull(self.loaded_version + 1)

    def downgrade(self) -> None:
        self.pull(self.loaded_version - 1)

    async def aupgrade(self) -> None:
        await self.apull(self.loaded_version + 1)

    async def adowngrade(self) -> None:
        await self.apull(self.loaded_version - 1)

    async def aupdate_all(self, version: Optional[int] = None) -> None:
        await self.aredis_client.publish(
            f"{state_manager.CHANNEL_NAME}:{self.name}",
            max(RESERVED_VERSIONS.LATEST, version),
        )

    async def aschedule_auto_updating(self) -> None:
        pubsub = self.aredis_client.pubsub(ignore_subscribe_messages=True)
        await pubsub.subscribe(f"{state_manager.CHANNEL_NAME}:{self.name}")

        while True:
            message = await pubsub.get_message()
            if message is not None:
                to_version = int(message["data"].decode())
                await self.apull(to_version)

            await asyncio.sleep(ASYNC_SLEEP_TIME)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.func(*args, **kwargs)
