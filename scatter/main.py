from scatter.scatter_function import ScatterFunction
from functools import wraps
import redis
import redis.asyncio as aredis
from typing import Callable, List, Optional
import asyncio
from scatter.state_manager import state_manager


def _load_function(name: str):
    scatter_obj = ScatterFunction(name=name)
    scatter_obj.pull()
    if state_manager.auto_updates:
        state_manager.scheduled_tasks.add(asyncio.create_task(scatter_obj.aschedule_auto_updating()))
    state_manager.loaded_functions[name] = scatter_obj


def init(
    auto_updates: bool = True,
    redis_url: Optional[str] = None, 
    functions_to_preload: Optional[List[str]] = None
):
    """
    auto_updates: Automatically update the loaded function if a new version of it is pushed.
                  Requires a running asyncio event loop.
    """

    # Making this function idempotent
    if state_manager.initialized:
        return

    state_manager.auto_updates = auto_updates

    if functions_to_preload is None:
        # Don't load any, instead let the `get` function load specific ones
        functions_to_preload = []

    if redis_url:
        # Always decode the responses
        redis_url.replace("decode_responses=False", "decode_responses=True")
        state_manager.redis_client = redis.from_url(redis_url)
        state_manager.aredis_client = aredis.from_url(redis_url)
    else:
        state_manager.redis_client = redis.Redis(protocol=state_manager.resp_protocol, decode_responses=True)
        state_manager.aredis_client = aredis.Redis(protocol=state_manager.resp_protocol, decode_responses=True)

    for name in functions_to_preload:
        _load_function(name)

    state_manager.initialized = True

def scatter(_func: Callable = None) -> ScatterFunction:
    scatter_obj = ScatterFunction(func=_func)
    return wraps(_func)(scatter_obj)


def get(name: str):
    if name not in state_manager.loaded_functions:
        _load_function(name)
    return state_manager.loaded_functions.get(name)


def cleanup():
    # Release references for garbage collection
    state_manager.scheduled_tasks.clear()
    state_manager.loaded_functions.clear()

    # Async client requires manual closing
    try:
        asyncio.create_task(state_manager.aredis_client.aclose())
    except RuntimeError:
        asyncio.run(state_manager.aredis_client.aclose())
