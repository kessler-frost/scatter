from scatter.scatter_function import ScatterFunction, AsyncScatterFunction
from functools import wraps, cache
import redis
import redis.asyncio as aredis
from typing import Union, Callable
import asyncio
from scatter.state import state


def init(async_mode: bool = True, redis_client: Union[aredis.Redis, redis.Redis] = None):
    # Making this function idempotent
    if state.redis_client is not None:
        return

    if redis_client is not None:
        state.redis_client = redis_client
        return

    state.async_mode = async_mode
    if async_mode:
        state.redis_client = aredis.Redis(protocol=state.resp_protocol)
    else:
        state.redis_client = redis.Redis(protocol=state.resp_protocol)


def scatter(_func: Callable = None) -> ScatterFunction:

    scatter_obj = (
        AsyncScatterFunction(redis_client=state.redis_client, func=_func) if state.async_mode else
        ScatterFunction(redis_client=state.redis_client, func=_func)
    )
    return wraps(_func)(scatter_obj)


# Caching so that the same object is returned.
# In non-async mode, the expectation is that the `pull` method will
# be called by the user themselves whenever they want, whereas
# in async mode automatic pulling ONLY when an update happens will happen
# and thus we don't need to run this function more than once
@cache
def assemble(name: str) -> Union[AsyncScatterFunction, ScatterFunction]:
    if state.async_mode:
        scatter_obj = AsyncScatterFunction(redis_client=state.redis_client, name=name)
        state.scheduled_tasks.add(asyncio.create_task(scatter_obj.schedule()))
    else:
        scatter_obj = ScatterFunction(redis_client=state.redis_client, name=name)
        scatter_obj.pull()
    return scatter_obj


def shutdown():
    # Close the redis connections
    if state.async_mode:
        state.scheduled_tasks.clear()
        asyncio.create_task(state.redis_client.aclose())
    else:
        state.redis_client.close()
