from scatter.models import Function, VersionedFunction
from redis_om import Migrator, get_redis_connection, NotFoundError
from typing import Callable
import cloudpickle
import inspect
import ulid


def save(function_: Callable) -> None:
    name = function_.__name__

    try:
        source = inspect.getsource(function_)
    except OSError:
        source = "Source code could not be retrieved"

    # Save the function
    function_id = str(ulid.ULID())
    r = get_redis_connection()
    r.set(function_id, cloudpickle.dumps(function_))

    try:
        current_function: Function = Function.find(Function.name == name).first()
    except NotFoundError:
        first_version = 0
        versioned_function = VersionedFunction(
            version=first_version,
            source=source,
            function_id=function_id
        ).save()

        new_function = Function(
            name=name,
            latest=first_version,
            saved_functions={
                first_version: versioned_function
            }
        ).save()

        Migrator().run()

        return new_function

    # If a function already exists
    new_version = current_function.latest
    versioned_function = VersionedFunction(
        version=new_version,
        source=source,
        function_id=function_id,
    )
    current_function.versioned_functions[new_version] = versioned_function
    return current_function.save()


def make_callable(name: str) -> Callable:
    ...
