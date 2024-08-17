import redis
import redis.asyncio as aredis
from typing import Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from scatter.scatter_function import ScatterFunction


class StateManager:
    def __init__(self) -> None:
        print("LOADED STATE MANAGER")

        self.auto_updates: bool = True

        # Default RESP protocol is 2 but I'm using 3 as it will support newer features and is backwards compatible
        self.resp_protocol: int = 3
        self.redis_client: Optional[redis.Redis] = None
        self.aredis_client: Optional[aredis.Redis] = None

        self.scheduled_tasks: set = set()

        self.loaded_functions: Dict[str, "ScatterFunction"] = {}

        self.initialized: bool = False

# Since this is part of the "state_manager" module, it is inherently singleton
state_manager = StateManager()
