import msgspec
import cloudpickle as pickle
import typing


def create_struct(function: typing.Callable) -> msgspec.Struct:

    # Get standard type hints
    msg_spec_hints = typing.get_type_hints(function)

    assert "return" in msg_spec_hints and len(msg_spec_hints) > 1, \
        "Typehint must be specified for all arguments and return value."

    msg_spec_hints = list(msg_spec_hints.items())

    # Handle `return` type hint
    msg_spec_hints[-1] = tuple([msg_spec_hints[-1][0], typing.Optional[msg_spec_hints[-1][1]], None])

    # Create struct
    Function = msgspec.defstruct(
        "Function",
        msg_spec_hints,
    )

    return Function

def enc_hook(obj: typing.Any) -> bytes:
    return pickle.dumps(obj)

def dec_hook(type: typing.Any, obj: bytes) -> typing.Any:
    return pickle.loads(obj)
