from mpire import WorkerPool
from functools import wraps, partial, lru_cache
from scatter.earth.storage import retrieve_callable
import cloudpickle as pickle
import zmq


#
#   Hello World server in Python
#   Binds REP socket to tcp://*:5555
#   Expects b"Hello" from client, replies with b"World"
#

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")


def job(func_name: str, *args, **kwargs):
    encoded_callable = retrieve_callable(func_name)
    func = pickle.loads(encoded_callable)
    return func(*args, **kwargs)


def submit_job(func_name: str, pool: WorkerPool, *args, **kwargs):
    return pool.apply(partial(job, func_name), args, kwargs)


while True:
    with WorkerPool(n_jobs=4) as pool:
        #  Wait for next request from client
        message = socket.recv_string()
        print("Received request:", message)

        submit_job

    #  Send reply back to client



if __name__ == '__main__':

    pool = get_pool()

    def task(a, b, c, d):
        return a + b + c + d

    # with WorkerPool(n_jobs=1) as pool:
    result = pool.apply(task, args=(1, 2), kwargs={'d': 4, 'c': 3})
    print(result)
    # pool.join()
