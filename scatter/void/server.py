from zero import ZeroServer

from scatter.earth.encoder_decoder import encoder, generate_decoder
from scatter.earth.struct_creation import (create_params_dict_from_struct,
                                           create_struct_class_from_type_hints)
from scatter.earth.structures import Function, FunctionExecute, Params
from scatter.ember.diskcache_backend import (delete_params,
                                             get_callable_function,
                                             get_type_hints, retrieve_params,
                                             retrieve_type_hints,
                                             store_callable, store_params,
                                             store_type_hints)
from scatter.void.constants import ZERO_SERVER_HOST, ZERO_SERVER_PORT

# TODO: Use redis_client's pipeline for performance improvement when doing multiple operations

app = ZeroServer(host=ZERO_SERVER_HOST, port=ZERO_SERVER_PORT)


@app.register_rpc
def scatter_function(function_: Function) -> None:

    name = function_["name"]
    encoded_callable = function_["encoded_callable"]
    encoded_type_hints = function_["encoded_type_hints"]

    store_callable(name, encoded_callable)
    store_type_hints(name, encoded_type_hints)


@app.register_rpc
def pull_type_hints(function_name: str) -> bytes:
    return retrieve_type_hints(function_name)


@app.register_rpc
def scatter_params(params: Params) -> None:

    message_id = params["message_id"]
    encoded_params = params["encoded_params"]

    store_params(message_id, encoded_params)


# NOTE: Only place where we use the `decoder` object - i.e. we need the dependencies
@app.register_rpc
def execute_function(function_execute: FunctionExecute) -> bytes:

    function_name = function_execute["function_name"]
    message_id = function_execute["message_id"]

    type_hints = get_type_hints(function_name)
    params_struct_class = create_struct_class_from_type_hints(
        function_name, type_hints, "ParamsStruct"
    )

    params_struct_obj = generate_decoder(params_struct_class).decode(retrieve_params(message_id))
    params_dict = create_params_dict_from_struct(params_struct_obj)

    # Remove the return key from the params_dict
    params_dict.pop("return")

    function = get_callable_function(function_name)

    result = function(**params_dict)

    delete_params(message_id)

    result_struct_class = create_struct_class_from_type_hints(
        function_name, {"result": type_hints["return"]}, "ResultStruct"
    )

    result_struct_obj = result_struct_class(result=result)
    return encoder.encode(result_struct_obj)


if __name__ == "__main__":
    print("Server started running...")
    app.run()
