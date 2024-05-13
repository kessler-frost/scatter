from functools import wraps
from typing import Callable

from scatter.earth.storage import store, delete
from scatter.earth.enc_dec import serialize_frames, deserialize_frames
import cloudpickle as pickle
import zmq

context = zmq.Context()

#  Socket to talk to server
print("Connecting to hello world server…")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")


def scatter(func: Callable) -> Callable:

    encoded_callable = pickle.dumps(func)
    store(encoded_callable, func.__name__)

    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


def make_callable(func_name: str) -> Callable:
    # TODO: Make it look like the actual function - using __signature__ and function_struct

    def wrapper(*args, **kwargs):
        #  Send a request
        socket.send_serialized((func_name, args, kwargs), serialize_frames)

        #  Get the reply.
        message = socket.recv_serialized(deserialize_frames)
        print("Received reply", message)
        return message

    return wrapper


def vaporize(func_name: str):
    try:
        delete(func_name)
    except KeyError:
        raise KeyError(f"Function {func_name} not found.") from None
