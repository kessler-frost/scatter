from zero import ZeroServer

from scatter.earth.encoder_decoder import (deserialize_any, encoder,
                                           generate_decoder)
from scatter.earth.struct_creation import (create_params_dict_from_struct,
                                           create_struct_class_from_type_hints)
from scatter.earth.structures import Function, FunctionExecute, Params
from scatter.ember.storage import (delete_params, retrieve_callable,
                                   retrieve_params, retrieve_type_hints,
                                   store_callable, store_params,
                                   store_type_hints)

# TODO: Use redis_client's pipeline for performance improvement when doing multiple operations

app = ZeroServer(port=4242)


@app.register_rpc
def scatter_function(function_: Function) -> None:
    name = function_.name
    store_callable(name, function_.encoded_callable_)
    store_type_hints(name, function_.encoded_type_hints)


@app.register_rpc
def get_type_hints(function_name: str) -> bytes:
    return retrieve_type_hints(function_name)


@app.register_rpc
def scatter_params(params: Params) -> None:
    store_params(params.message_id, params.encoded_params)


# NOTE: Only place where we use the `decoder` object - i.e. we need the dependencies
@app.register_rpc
def execute_function(function_execute: FunctionExecute) -> bytes:
    # The typing has been verified on the client side already
    # thus, we can safely decode the params without worrying about their type

    type_hints = deserialize_any(None, retrieve_type_hints(function_execute.function_name))
    params_struct_class = create_struct_class_from_type_hints(
        function_execute.function_name, type_hints, "ParamsStruct"
    )

    params_struct_obj = generate_decoder(params_struct_class).decode(retrieve_params(function_execute.message_id))
    params_dict = create_params_dict_from_struct(params_struct_obj)

    function = deserialize_any(retrieve_callable(function_execute.function_name))

    result = function(**params_dict)

    delete_params(function_execute.message_id)

    result_struct_class = create_struct_class_from_type_hints(
        function_execute.function_name, {"result": type_hints["return"]}, "ResultStruct"
    )

    result_struct_obj = result_struct_class(result=result)
    return encoder.encode(result_struct_obj)


if __name__ == "__main__":
    app.run()
