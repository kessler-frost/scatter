from scatter.models import Function, VersionedFunction
from redis_om import Migrator, get_redis_connection, NotFoundError
from redis import ResponseError
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

    try:
        current_function: Function = Function.find(Function.name == name).first()
    except (NotFoundError, ResponseError):
        first_version = 0

        # Save the function
        function_id = str(ulid.ULID())
        r = get_redis_connection()
        r.set(function_id, cloudpickle.dumps(function_))

        versioned_function = VersionedFunction(
            version=first_version,
            source=source,
        ).save()

        new_function = Function(
            name=name,
            latest=first_version,
            versioned_functions={
                first_version: versioned_function
            }
        ).save()

        Migrator().run()

        return new_function

    # If a function already exists
    new_version = current_function.latest + 1

    # Save the function
    function_id = str(ulid.ULID())
    r = get_redis_connection()
    r.set(function_id, cloudpickle.dumps(function_))

    versioned_function = VersionedFunction(
        version=new_version,
        source=source,
    ).save()

    current_function.latest = new_version
    current_function.versioned_functions[new_version] = versioned_function
    return current_function.save()


def make_callable(name: str) -> Callable:
    ...
