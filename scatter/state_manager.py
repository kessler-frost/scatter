import redis
import redis.asyncio as aredis
from typing import Union, Dict
from scatter.scatter_function import AsyncScatterFunction, ScatterFunction


class StateManager:
    def __init__(self) -> None:
        self.async_mode: bool = True

        # Default RESP protocol is 2 but I'm using 3 as it will support newer features and is backwards compatible
        self.resp_protocol: int = 3
        self.redis_client: Union[None, redis.Redis, aredis.Redis] = None

        self.scheduled_tasks: set = set()

        self.loaded_functions: Dict[str, Union[AsyncScatterFunction, ScatterFunction]] = {}

state_manager = StateManager()
