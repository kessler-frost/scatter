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
        if self.redis_client is None:
            raise RuntimeError("state_manager.redis_client is not initialized")
        self.pipe = self.redis_client.pipeline()

        self.aredis_client = state_manager.aredis_client
        if self.aredis_client is None:
            raise RuntimeError("state_manager.aredis_client is not initialized")
        self.apipe = self.aredis_client.pipeline()

        if not func and not name:
            raise ValueError("Either `name` or `func` must be passed")

        self.name = name
        self.func = func
        self._source = None

        if self.func is not None:
            # Update the name to function's name irrespective of the passed in name
            self.name = self.func.__name__
            self._source = inspect.getsource(self.func)

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

    def first_push(self) -> None:
        latest_version: Union[str, None] = self.latest_version(raw=True)

        # Only do something if the function doesn't exist
        if latest_version is None:
            ser_func: bytes = cloudpickle.dumps(self.func)
            self.pipe.hset(state_manager.FUNC_VERSIONS_HASH_NAME, self.name, RESERVED_VERSIONS.INITIAL)
            self.pipe.hset(
                f"{state_manager.ROOT_PREFIX}:{self.name}",
                mapping={"ser_func": ser_func, "source": self.source},
            )
            self.pipe.execute()
            self._loaded_version = RESERVED_VERSIONS.INITIAL

    async def afirst_push(self) -> None:
        latest_version: Union[str, None] = await self.alatest_version(raw=True)

        # Only do something if the function doesn't exist
        if latest_version is None:
            ser_func: bytes = cloudpickle.dumps(self.func)
            await self.apipe.hset(state_manager.FUNC_VERSIONS_HASH_NAME, self.name, RESERVED_VERSIONS.INITIAL)
            await self.apipe.hset(
                f"{state_manager.ROOT_PREFIX}:{self.name}",
                mapping={"ser_func": ser_func, "source": self.source},
            )
            await self.apipe.execute()
            self._loaded_version = RESERVED_VERSIONS.INITIAL

    def sync(self) -> None:
        latest_version: Union[str, None] = self.latest_version(raw=True)

        # Only do something if the function already exists
        if latest_version is not None:
            ser_func: bytes = cloudpickle.dumps(self.func)
            self.pipe.hset(
                f"{state_manager.ROOT_PREFIX}:{self.name}",
                mapping={"ser_func": ser_func, "source": self.source},
            )

            self.pipe.publish(f"{state_manager.CHANNEL_NAME}:{self.name}", RESERVED_VERSIONS.LATEST)

            self.pipe.execute()
            self._loaded_version = int(latest_version)

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

        new_version = int(latest_version or RESERVED_VERSIONS.INITIAL - 1) + 1

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

        new_version = int(latest_version or RESERVED_VERSIONS.INITIAL - 1) + 1

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
        # Guard for the upgrade/downgrade borders
        if version == RESERVED_VERSIONS.NO_CHANGE:
            return

        latest_version = self.latest_version(raw=True)
        if latest_version is None:
            raise KeyError(f"Function `{self.name}` doesn't exist")
        else:
            latest_version = int(latest_version)

        if (
            version is None
            or version == latest_version
            # In case there doesn't exist any other version, thus no `{name}:{version}` hash exists
            or latest_version == RESERVED_VERSIONS.INITIAL
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
                version = max(RESERVED_VERSIONS.INITIAL, version)
            mapping = dict_decode(
                self.redis_client.hgetall(
                    f"{state_manager.ROOT_PREFIX}:{self.name}:{version}",
                )
            )

            # If trying to pull a version which no longer exists
            if len(mapping) == 0:
                raise KeyError(f"`{version}` version of the function `{self.name}` no longer exists")

        self._loaded_version = version
        self._source = mapping["source"]
        self.func = cloudpickle.loads(mapping["ser_func"])

        # Update the "look" of the instance
        update_wrapper(self, self.func)

    async def apull(self, version: Optional[int] = None) -> None:
        # Guard for the upgrade/downgrade borders
        if version == RESERVED_VERSIONS.NO_CHANGE:
            return

        latest_version = await self.alatest_version(raw=True)
        if latest_version is None:
            raise KeyError(f"Function `{self.name}` doesn't exist")
        else:
            latest_version = int(latest_version)

        if (
            version is None
            or version == latest_version
            or version == RESERVED_VERSIONS.LATEST
            # In case there doesn't exist any other version, thus no `{name}:{version}` hash exists
            or latest_version == RESERVED_VERSIONS.INITIAL
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
                version = max(RESERVED_VERSIONS.INITIAL, version)
            mapping = dict_decode(
                await self.aredis_client.hgetall(
                    f"{state_manager.ROOT_PREFIX}:{self.name}:{version}",
                )
            )

            # If trying to pull a version which no longer exists
            if len(mapping) == 0:
                raise KeyError(f"`{version}` version of the function `{self.name}` no longer exists")

        self._loaded_version = version
        self._source = mapping["source"]
        self.func = cloudpickle.loads(mapping["ser_func"])

        # Update the "look" of the instance
        update_wrapper(self, self.func)

    def delete(self, older_than: Optional[int] = None) -> None:

        latest_version = self.latest_version(raw=True)
        if latest_version is not None:

            latest_version = int(latest_version)

            if older_than is None:
                # Delete the loaded function
                del state_manager.loaded_functions[self.name]

                # Delete all
                self.pipe.hdel(state_manager.FUNC_VERSIONS_HASH_NAME, self.name)
                self.pipe.delete(f"{state_manager.ROOT_PREFIX}:{self.name}")

                # For deleting others
                older_than = latest_version

            elif older_than == RESERVED_VERSIONS.LATEST:
                older_than = latest_version

            elif older_than >= latest_version:
                older_than = min(latest_version, older_than)

            elif older_than < RESERVED_VERSIONS.INITIAL:
                older_than = max(RESERVED_VERSIONS.INITIAL, older_than)

            if latest_version != RESERVED_VERSIONS.INITIAL:
                self.pipe.delete(*[f"{state_manager.ROOT_PREFIX}:{self.name}:{version}" for version in range(RESERVED_VERSIONS.INITIAL, older_than)])

            self.pipe.execute()

    async def adelete(self, older_than: Optional[int] = None) -> None:
        latest_version = await self.alatest_version(raw=True)
        if latest_version is not None:

            latest_version = int(latest_version)

            if older_than is None:
                # Delete the loaded function
                del state_manager.loaded_functions[self.name]

                # Delete all
                await self.apipe.hdel(state_manager.FUNC_VERSIONS_HASH_NAME, self.name)
                await self.apipe.delete(f"{state_manager.ROOT_PREFIX}:{self.name}")

                # For deleting others
                older_than = latest_version

            elif older_than == RESERVED_VERSIONS.LATEST:
                older_than = latest_version

            elif older_than >= latest_version:
                older_than = min(latest_version, older_than)

            elif older_than < RESERVED_VERSIONS.INITIAL:
                older_than = max(RESERVED_VERSIONS.INITIAL, older_than)

            if latest_version != RESERVED_VERSIONS.INITIAL:
                await self.apipe.delete(*[f"{state_manager.ROOT_PREFIX}:{self.name}:{version}" for version in range(RESERVED_VERSIONS.INITIAL, older_than)])

            await self.apipe.execute()

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
