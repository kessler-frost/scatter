from scatter.models import Function, VersionedFunction
from redis_om import Migrator, get_redis_connection, NotFoundError
from redis import ResponseError
from pydantic import validate_call
from typing import Callable
import cloudpickle
import inspect


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

        versioned_function = VersionedFunction(
            version=first_version,
            source=source,
        ).save()

        # Save the function
        r = get_redis_connection()
        r.set(versioned_function.pk, cloudpickle.dumps(function_))

        new_function = Function(
            name=name,
            current_version=first_version,
            versioned_functions={
                first_version: versioned_function
            }
        ).save()

        Migrator().run()

        return new_function

    # If a function already exists
    new_version = current_function.current_version + 1

    versioned_function = VersionedFunction(
        version=new_version,
        source=source,
    ).save()

    # Save the function
    r = get_redis_connection()
    r.set(versioned_function.pk, cloudpickle.dumps(function_))


    current_function.current_version = new_version
    current_function.versioned_functions[new_version] = versioned_function
    return current_function.save()


def _get_function(name: str) -> Function:
    try:
        return Function.find(Function.name == name).first()
    except (NotFoundError, ResponseError):
        raise NotFoundError(f"Function by the name {name} could not be found.")


def make_callable(name: str) -> Callable:
    
    current_function = _get_function(name)

    function_id = current_function.versioned_functions[
        current_function.current_version
        ].pk

    r = get_redis_connection(decode_responses=False)
    ser_func = r.get(function_id)
    return validate_call(cloudpickle.loads(ser_func))
