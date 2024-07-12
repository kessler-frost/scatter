import warnings
warnings.filterwarnings("ignore", category=UserWarning)

from redis_om import HashModel
from pydantic import field_serializer, field_validator, computed_field
import cloudpickle
from typing import Union, Callable
from inspect import Signature
import inspect


class BaseHashModel(HashModel):
    # In case we want to modify anything from the HashModel
    # or have something in commong for all subsequent models
    ...


class FunctionModel(BaseHashModel):
    function_: Callable

    model_config = {
        "arbitrary_types_allowed": True
    }

    @computed_field
    def name(self) -> str:
        return self.function_.__name__
    
    @computed_field
    def signature(self) -> Signature:
        return inspect.signature(self.function_)

    @field_serializer("signature", "function_", when_used="always")
    def serialize(val: Union[Callable, Signature]) -> bytes:
        return cloudpickle.dumps(val)

    @field_validator("signature", "function_", mode="before")
    @classmethod
    def deserialize(cls, val: Union[bytes, Callable, Signature]) -> Signature:
        if type(val) is bytes:
            return cloudpickle.loads(val)
        else:
            return val
