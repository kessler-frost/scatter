from mpire import WorkerPool
from functools import partial
from scatter.earth.storage import retrieve_callable
from scatter.earth.enc_dec import deserialize_frames, serialize_frames
import cloudpickle as pickle
import zmq


context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")


def job(func_name: str, *args, **kwargs):
    encoded_callable = retrieve_callable(func_name)
    func = pickle.loads(encoded_callable)
    return func(*args, **kwargs)


if __name__ == "__main__":

    while True:
        with WorkerPool(n_jobs=4) as pool:
            #  Wait for next request from client
            message = socket.recv_serialized(deserialize_frames)
            print("Received request:", message)

            func_name, args, kwargs = message
            result = pool.apply(partial(job, func_name), args, kwargs)

            socket.send_serialized(result, serialize_frames)
