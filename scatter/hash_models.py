import warnings
warnings.filterwarnings("ignore", category=UserWarning)

from redis_om import HashModel
from pydantic import field_serializer, field_validator
import cloudpickle
from typing import Union
from inspect import Signature

class BaseHashModel(HashModel):
    # In case we want to modify anything from the HashModel
    # or have something in commong for all subsequent models
    ...


class FunctionModel(BaseHashModel):
    name: str
    signature: Signature

    model_config = {
        "arbitrary_types_allowed": True
    }

    @field_serializer("signature", when_used="always")
    def serialize_signature_function_signature(signature: Signature) -> bytes:
        return cloudpickle.dumps(signature)

    @field_validator("signature", mode="before")
    @classmethod
    def deserialize_signature(cls, signature: Union[bytes, Signature]) -> Signature:
        if type(signature) is bytes:
            return cloudpickle.loads(signature)
        else:
            return signature
