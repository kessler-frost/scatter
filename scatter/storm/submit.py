from mpire import WorkerPool
from functools import wraps
from scatter.earth.storage import retrieve_callable
import cloudpickle as pickle


pool = WorkerPool(n_jobs=4)


def submit_job(func_name: str):

    function_callable = pickle.dumps(retrieve_callable(func_name))

    @wraps(function_callable)
    def wrapper(*args, **kwargs):
        return pool.apply(function_callable, args, kwargs)

    return wrapper
