import dramatiq

from dramatiq.brokers.redis import RedisBroker


redis_broker = RedisBroker(host="127.0.0.1", port=6379, db=0)
dramatiq.set_broker(redis_broker)


@dramatiq.actor
def task_execution(func_name: str, args_ref: str, kwargs_ref: str):
    
