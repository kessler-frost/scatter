import logging
from functools import wraps
from typing import Callable, get_type_hints

import shortuuid
from zero import ZeroClient

from scatter.brew.constants import ZERO_SERVER_HOST, ZERO_SERVER_PORT
from scatter.earth.encoder_decoder import (deserialize_any, encoder,
                                           generate_decoder, serialize_any)
from scatter.earth.struct_creation import create_struct_class_from_type_hints
from scatter.earth.structures import Function, FunctionExecute, Params

# Set the logging level to ERROR to avoid unnecessary logs from the Zero library
logging.getLogger().setLevel(logging.ERROR)

zero_client = ZeroClient(host=ZERO_SERVER_HOST, port=ZERO_SERVER_PORT)


def scatter(func: Callable) -> Callable:

    function_struct = Function(
        name=func.__name__,
        encoded_callable=serialize_any(func),
        encoded_type_hints=serialize_any(get_type_hints(func)),
    )

    # Doesn't return anything
    zero_client.call("scatter_function", function_struct)

    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


def vaporize(func_name: str) -> None:
    zero_client.call("delete_callable", func_name)


def rollback(func_name: str) -> None:
    zero_client.call("rollback_callable", func_name)


def current_version(func_name: str) -> int:
    return zero_client.call("get_current_version", func_name)


def make_callable(func_name: str) -> Callable:

    encoded_type_hints = zero_client.call("pull_type_hints", func_name)
    type_hints = deserialize_any(None, encoded_type_hints)

    params_struct_class = create_struct_class_from_type_hints(
        func_name, type_hints, "ParamsStruct"
    )

    def wrapper(*args, **kwargs):
        decoder = generate_decoder(params_struct_class)

        params_struct_obj = params_struct_class(*args, **kwargs)

        encoded_params = encoder.encode(params_struct_obj)

        # Do validation by decoding the params
        decoder.decode(encoded_params)

        # Proceed if validation is successful
        message_id = shortuuid.uuid()
        params = Params(message_id=message_id, encoded_params=encoded_params)

        zero_client.call("scatter_params", params)

        # Proceed to execute the function
        function_execute = FunctionExecute(function_name=func_name, message_id=message_id)

        result_struct_class = create_struct_class_from_type_hints(
            function_execute.function_name, {"result": type_hints["return"]}, "ResultStruct"
        )

        encoded_result = zero_client.call("execute_function", function_execute)

        result = generate_decoder(result_struct_class).decode(encoded_result)

        return result.result

    return wrapper
