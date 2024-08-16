from scatter.scatter_function import ScatterFunction, AsyncScatterFunction
from functools import wraps, cache
import redis
import redis.asyncio as aredis
from typing import Union, Callable, List
import asyncio
from scatter.state_manager import state_manager


def init(
    async_mode: bool = True,
    redis_client: Union[aredis.Redis, redis.Redis] = None,
    functions_to_load: List[str] = None
):
    # Making this function idempotent
    if state_manager.redis_client is not None:
        return

    if redis_client is not None:
        state_manager.redis_client = redis_client
        return

    if functions_to_load is not None:
        functions_to_load = set(functions_to_load)

    state_manager.async_mode = async_mode
    if async_mode:
        state_manager.redis_client = aredis.Redis(protocol=state_manager.resp_protocol)
        for name in functions_to_load:
            scatter_obj = AsyncScatterFunction(redis_client=state_manager.redis_client, name=name)
            state_manager.scheduled_tasks.add(asyncio.create_task(scatter_obj.schedule()))
            state_manager.loaded_functions[name] = scatter_obj
    else:
        state_manager.redis_client = redis.Redis(protocol=state_manager.resp_protocol)
        for name in functions_to_load:
            scatter_obj = ScatterFunction(redis_client=state_manager.redis_client, name=name)
            scatter_obj.pull()


def scatter(_func: Callable = None) -> Union[AsyncScatterFunction, ScatterFunction]:
    scatter_obj = (
        AsyncScatterFunction(redis_client=state_manager.redis_client, func=_func) if state_manager.async_mode else
        ScatterFunction(redis_client=state_manager.redis_client, func=_func)
    )
    return wraps(_func)(scatter_obj)


# Caching so that the same object is returned.
# In non-async mode, the expectation is that the `pull` method will
# be called by the user themselves whenever they want, whereas
# in async mode ONLY pull when an update happens and thus we don't 
# # need to run this function more than once
@cache
def get(name: str):
    return state_manager.loaded_functions.get(name)


def shutdown():
    # Close the redis connections
    if state_manager.async_mode:
        state_manager.scheduled_tasks.clear()
        asyncio.create_task(state_manager.redis_client.aclose())
    else:
        state_manager.redis_client.close()
