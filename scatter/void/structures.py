import msgspec

# TODO: Can use `array_like=True` in the Struct definition to improve performance


class Function(msgspec.Struct):
    name: str
    encoded_callable_: bytes
    encoded_type_hints: bytes


class Params(msgspec.Struct):
    message_id: str
    encoded_params: bytes


class FunctionExecute(msgspec.Struct):
    function_name: str
    message_id: str
