import msgspec
from zero import ZeroServer

from scatter.earth.storage import (delete_params, retrieve_callable,
                                   retrieve_params, retrieve_type_hints,
                                   store_callable, store_params,
                                   store_type_hints)

# TODO: Use redis_client's pipeline for performance improvement

app = ZeroServer(port=4242)


class Function(msgspec.Struct):
    name: str
    callable_: bytes
    type_hints: bytes


@app.register_rpc
def scatter_function(function_: Function) -> None:
    name = function_.name
    store_callable(name, function_.callable_)
    store_type_hints(name, function_.type_hints)


@app.register_rpc
def get_type_hints(function_name: str) -> bytes:
    return retrieve_type_hints(function_name)


@app.register_rpc
def scatter_params(message_id: str, args: bytes, kwargs: bytes) -> None:
    store_params(message_id, args, kwargs)


@app.register_rpc
def execute_function(function_name: str, message_id: str) -> bytes:
    args, kwargs = retrieve_params(message_id)
    function = retrieve_callable(function_name)

    result = function(*args, **kwargs)

    delete_params(message_id)

    return result

if __name__ == "__main__":
    app.run()
