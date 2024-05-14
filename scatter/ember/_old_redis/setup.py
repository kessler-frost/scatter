import dramatiq
from dramatiq.brokers.redis import RedisBroker

from scatter.ember.constants import (PRIO_HI, PRIO_MED, REDIS_DB, REDIS_HOST,
                                     REDIS_PASSWORD, REDIS_PORT)


redis_broker = RedisBroker(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, password=REDIS_PASSWORD)
dramatiq.set_broker(redis_broker)


type_hint_actor_options = {
    "actor_name": "type_hint_actor",
    "queue_name": "type_hint_queue",
    "priority": PRIO_HI,
}


task_execution_actor_options = {
    "actor_name": "task_execution_actor",
    "queue_name": "task_execution_queue",
    "priority": PRIO_MED,
}


@dramatiq.actor(**type_hint_actor_options)
def get_type_hints(func_name: str):
    ...


@dramatiq.actor(**task_execution_actor_options)
def execute_function(func_name: str, args_ref: str, kwargs_ref: str):
    ...
