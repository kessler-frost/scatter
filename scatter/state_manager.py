import redis
import redis.asyncio as aredis
from typing import Dict, Optional, TYPE_CHECKING
from pprint import pformat

if TYPE_CHECKING:
    from scatter.scatter_function import ScatterFunction


class StateManager:
    def __init__(self) -> None:
        self.prefix: Optional[str] = None

        self.auto_updates: bool = True

        # Default RESP protocol is 2 but I'm using 3 as it will support newer features and is backwards compatible
        self.resp_protocol: int = 3
        self.redis_client: Optional[redis.Redis] = None
        self.aredis_client: Optional[aredis.Redis] = None

        self.scheduled_tasks: set = set()

        self.loaded_functions: Dict[str, "ScatterFunction"] = {}

        self.initialized: bool = False

        # Key names:
        self._ROOT_PREFIX = "scatter"
        self._FUNC_VERSIONS_HASH_NAME = "func_versions_hash"
        self._CHANNEL_NAME = "channel"

    @property
    def ROOT_PREFIX(self):
        return ":".join([self._ROOT_PREFIX, self.prefix])

    @property
    def FUNC_VERSIONS_HASH_NAME(self):
        return ":".join([self.ROOT_PREFIX, self._FUNC_VERSIONS_HASH_NAME])

    @property
    def CHANNEL_NAME(self):
        return ":".join([self.ROOT_PREFIX, self._CHANNEL_NAME])

    def __repr__(self) -> str:
        return pformat(self.__dict__)


# Since this is part of the "state_manager" module, it is inherently singleton
state_manager = StateManager()
