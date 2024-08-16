import enum


FUNC_VERSIONS_HASH = "func_versions_hash"
ASYNC_SLEEP_TIME = 0.001


class RESERVED_VERSIONS(enum.IntEnum):
    NO_CHANGE = 0
    LATEST = -1
