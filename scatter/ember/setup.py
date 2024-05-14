import dramatiq

from dramatiq.brokers.redis import RedisBroker


redis_broker = RedisBroker(host="127.0.0.1", port=6379, db=0)
dramatiq.set_broker(redis_broker)


type_hint_actor_options = {
    "actor_name": "type_hint_actor",
    "queue_name": "type_hint_queue",
    "priority": 1,
}


task_execution_actor_options = {
    "actor_name": "task_execution_actor",
    "queue_name": "task_execution_queue",
    "priority": 2,
}


@dramatiq.actor(**type_hint_actor_options)
def get_type_hints(func_name: str):
    ...


@dramatiq.actor(**task_execution_actor_options)
def execute_function(func_name: str, args_ref: str, kwargs_ref: str):
    ...
