from typing import Dict, Any


ASYNC_SLEEP_TIME = 0.001


class RESERVED_VERSIONS:
    LATEST = -1
    NO_CHANGE = 0
    INITIAL = 1


def safe_decode(obj: bytes) -> Any:
    try:
        return obj.decode()
    except Exception:
        return obj


def dict_decode(encoded_dict: Dict[bytes, bytes]) -> Dict[str, Any]:
    return {safe_decode(k): safe_decode(v) for k, v in encoded_dict.items()}
