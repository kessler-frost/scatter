from scatter.scatter_function import ScatterFunction, AsyncScatterFunction
from functools import wraps, cache
import redis
import redis.asyncio as aredis
from typing import Union
import asyncio


_async_mode: bool = False


# Default RESP protocol is 2 but I'm using 3 as it will support newer features and is backwards compatible
_resp_protocol: int = 3
_redis_client: Union[None, redis.Redis, aredis.Redis] = None


_scheduled_tasks = set()


def init(async_: bool = False):
    global _redis_client
    global _async_mode
    _async_mode = async_

    if _redis_client is not None:
        return

    if _async_mode:
        _redis_client = aredis.Redis(protocol=_resp_protocol)
    else:
        _redis_client = redis.Redis(protocol=_resp_protocol)


def scatter(_func = None) -> ScatterFunction:
    global _redis_client
    global _async_mode

    scatter_obj = (
        AsyncScatterFunction(redis_client=_redis_client, func=_func) if _async_mode else
        ScatterFunction(redis_client=_redis_client, func=_func)
    )
    return wraps(_func)(scatter_obj)


# Caching so that the same object is returned.
# In non-async mode, the expectation is that the `pull` method will
# be called by the user themselves whenever they want, whereas
# in async mode automatic pulling ONLY when an update happens will happen
# and thus we don't need to run this function more than once
@cache
def assemble(name: str) -> Union[AsyncScatterFunction, ScatterFunction]:
    global _redis_client
    global _async_mode

    if _async_mode:
        scatter_obj = AsyncScatterFunction(redis_client=_redis_client, name=name)
        _scheduled_tasks.add(asyncio.create_task(scatter_obj.pull()))
        _scheduled_tasks.add(asyncio.create_task(scatter_obj.schedule()))
    else:
        scatter_obj = ScatterFunction(redis_client=_redis_client, name=name)
        scatter_obj.pull()
    return scatter_obj


def shutdown():
    global _redis_client
    global _async_mode

    # Close the redis connections
    if _async_mode:
        _scheduled_tasks.clear()
        asyncio.create_task(_redis_client.aclose())
    else:
        _redis_client.close()
