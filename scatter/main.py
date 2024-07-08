import inspect
import sys
import cloudpickle
from typing import Dict, Callable, Any


def sample(i: int, j: float = 4.0) -> list[float]:
    return i + j


def extract_info(func: Callable) -> Dict[str, Any]:
    sig = inspect.signature(func)
    params = dict(sig.parameters)

    params_info = {}
    for k, v in params.items():
        params_info[k] = {
            "annotation": v.annotation,
            "default": v.default
        }
    return_type = sig.return_annotation
    return {
        "params_info": params_info,
        "return_type": return_type
    }


info = extract_info(sample)

print(info)

print(type(info["params_info"]["i"]["annotation"]))

