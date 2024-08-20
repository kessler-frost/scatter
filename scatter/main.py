from scatter.scatter_function import ScatterFunction
from functools import wraps
import redis
import redis.asyncio as aredis
from typing import Callable, List, Optional
import asyncio
from scatter.state_manager import state_manager


def _load_function(name: str) -> None:
    """
    Load the function in memory to add to `state_manager.loaded_functions` dictionary

    Args:
        name: Name of the function in the redis store
    """

    scatter_obj = ScatterFunction(name=name)
    scatter_obj.pull()
    if state_manager.auto_updates:
        state_manager.scheduled_tasks.add(
            asyncio.create_task(scatter_obj.aschedule_auto_updating())
        )
    state_manager.loaded_functions[name] = scatter_obj


def init(
    prefix: Optional[str] = None,
    auto_updates: bool = True,
    redis_url: Optional[str] = None,
    functions_to_preload: Optional[List[str]] = None,
) -> None:
    """
    Initialize and set up `scatter`
    
    Args:
        prefix: Prefix to use to determine which set of functions does the user wants to operate upon.
                For e.g. there might be 2 `sample_task`'s saved. One belonging to `red_project` and
                another to `blue_project` in the same Redis store, by specifying `prefix="red_project"`
                only that set of functions will be operated upon.
                
                This can also be used as a way to denote which user's functions should be used in case you have
                a shared Redis store with other users, using `prefix=Thor` or `prefix=Steve`.

        auto_updates: Automatically update the loaded function if a new version of it is pushed.
                      Requires a running asyncio event loop.
        
        redis_url: Redis url to use in case a redis instance is deployed somewhere other than localhost:6379

        functions_to_preload: List of function names that can be preloaded to save some time for the first `scatter.get`
                              call for those functions.
    """

    # Making this function idempotent
    if state_manager.initialized:
        return

    state_manager.prefix = prefix or "hal-jordan"
    state_manager.auto_updates = auto_updates

    if functions_to_preload is None:
        # Don't load any, instead let the `get` function load specific ones
        functions_to_preload = []

    if redis_url:
        # Never decode the responses as we will do a safer version of decoding afterwards
        redis_url = redis_url.replace("decode_responses=True", "decode_responses=False")
        state_manager.redis_client = redis.from_url(redis_url)
        state_manager.aredis_client = aredis.from_url(redis_url)
    else:
        state_manager.redis_client = redis.Redis(protocol=state_manager.resp_protocol)
        state_manager.aredis_client = aredis.Redis(protocol=state_manager.resp_protocol)

    for name in functions_to_preload:
        _load_function(name)

    state_manager.initialized = True


def scatter(_func: Callable = None) -> ScatterFunction:
    """
    Decorator to make the function ready for management with `scatter`.

    Creates and returns a callable `ScatterFunction` object.

    Example:
    ```
    @scatter
    def sample(a: int, b: int):
        return a * b
    
    # Now you can either call the function normally
    # as you would in the absence of `scatter` decorator
    
    res = sample(2, 21)
    print(res)  # prints 42

    # Or you save/update the function definition by `push`
    
    sample.push()

    # Or load the most up to date function definition by `pull`
    
    sample.pull()

    # You can also specify which particular version you would like to load
    
    sample.pull(version=1)

    ```

    Args:
        _func: Function which you want to scatter i.e. manage using `scatter`
    """

    scatter_obj = ScatterFunction(func=_func)
    return wraps(_func)(scatter_obj)


def get(name: str) -> ScatterFunction:
    """
    Get the callable function by name.
    
    This first checks whether the function is already in memory
    then returns that, otherwise pulls from the redis store and loads
    into memory for current, and future uses.

    Thus, this function can be called any number of times without impacting
    the performance or network bandwidth cost apart from the first time.

    Args:
        name: Name of the saved function to load
    """

    if name not in state_manager.loaded_functions:
        _load_function(name)
    return state_manager.loaded_functions.get(name)


def cleanup():
    """
    Cleanup by releasing the memory of all the loaded
    functions and disconnecting from the redis instance.

    Calling this function is optional but recommended once
    you're done using `scatter`. If running on a server,
    you can put this in shutdown part of the server lifecycle.

    """

    # Release references for garbage collection
    state_manager.scheduled_tasks.clear()
    state_manager.loaded_functions.clear()

    # Async client requires manual closing
    try:
        asyncio.create_task(state_manager.aredis_client.aclose())
    except RuntimeError:  # In case there's no running loop
        asyncio.run(state_manager.aredis_client.aclose())
