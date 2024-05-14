import msgspec
from typing import Dict, Any, Optional, get_type_hints


def create_struct_from_type_hints(func_name: str, type_hints: Dict[str, Any]) -> msgspec.Struct:

    # This will make it a list of tuples - (name, type)
    msg_spec_hints = list(type_hints.items())

    # Since the last element will be the "return" type hint,
    # thus this will become from ("return", <type>) to ("return", Optional[<type>], None)
    msg_spec_hints[-1] = tuple([msg_spec_hints[-1][0], Optional[msg_spec_hints[-1][1]], None])

    # Create struct
    Struct = msgspec.defstruct(
        f"Struct_{func_name}",
        msg_spec_hints,
    )

    return Struct


def create_struct_from_callable(func: callable) -> msgspec.Struct:
    return create_struct_from_type_hints(func.__name__, get_type_hints(func))
