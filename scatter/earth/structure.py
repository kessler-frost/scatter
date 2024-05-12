import msgspec
import typing
from scatter.earth.key_helpers import func_name_to_struct_name


def create_struct(function: typing.Callable) -> msgspec.Struct:

    # Get standard type hints
    msg_spec_hints = typing.get_type_hints(function)

    assert "return" in msg_spec_hints and len(msg_spec_hints) > 1, \
        "Typehint must be specified for all arguments and return value."

    # Get msgspec types
    msg_spec_types: typing.Tuple = msgspec.inspect.multi_type_info(msg_spec_hints.values())

    # Convert to msgspec hints
    msg_spec_hints = tuple(zip(msg_spec_hints.keys(), msg_spec_types))

    # Create struct
    Function = msgspec.defstruct(
        func_name_to_struct_name(function.__name__),
        msg_spec_hints,
    )

    return Function
