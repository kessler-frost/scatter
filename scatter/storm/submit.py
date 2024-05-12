from mpire import WorkerPool
import typing
from scatter.earth.storage import cache, index, retrieve_struct, decode
from scatter.earth.key_helpers import func_name_to_callable_key
import msgspec


pool = WorkerPool(n_jobs=4)


@cache.memoize()
def generate_decoder(function_struct: msgspec.Struct):
    decoder = msgspec.msgpack.Decoder(type=function_struct, dec_hook=decode)
    return decoder


def create_job(encoded_struct_obj: bytes, func_name: str) -> typing.Callable:

    encoded_struct = retrieve_struct(func_name)
    function_struct = decode(encoded_struct)

    decoder = generate_decoder(function_struct)

    struct_obj = decoder.decode(encoded_struct_obj)

    function_callable = decode(cache[func_name_to_callable_key(func_name, version=index[func_name])])

    kwargs = {f: getattr(struct_obj, f) for f in struct_obj.__struct_fields__}

    return function_callable(**kwargs)


def submit_job(encoded_struct_obj: bytes, func_name: str):
    job = create_job(encoded_struct_obj, func_name)
    return pool.apply(job)
