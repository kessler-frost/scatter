from typing import Any, Dict, Optional, get_type_hints

import msgspec


def create_struct_class_from_type_hints(
        func_name: str, type_hints: Dict[str, Any], prefix: str = "Struct"
) -> msgspec.Struct.__class__:

    # This will make it a list of tuples - (name, type)
    msg_spec_hints = list(type_hints.items())

    # Since the last element will be the "return" type hint,
    # thus this will become from ("return", <type>) to ("return", Optional[<type>], None)
    msg_spec_hints[-1] = tuple([msg_spec_hints[-1][0], Optional[msg_spec_hints[-1][1]], None])

    # Create struct
    Struct = msgspec.defstruct(
        f"{prefix}_{func_name}",
        msg_spec_hints,
        # TODO: Can use `array_like=True` in here to improve performance
    )

    return Struct


def create_params_struct_class_from_callable(func: callable) -> msgspec.Struct.__class__:
    return create_struct_class_from_type_hints(func.__name__, get_type_hints(func), "ParamsStruct")


def create_params_dict_from_struct(struct_obj: msgspec.Struct) -> Dict[str, Any]:
    return {f: getattr(struct_obj, f) for f in struct_obj.__struct_fields__}
