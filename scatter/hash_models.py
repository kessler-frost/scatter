import warnings
warnings.filterwarnings("ignore", category=UserWarning)

from redis_om import HashModel


class BaseHashModel(HashModel):
    # In case we want to modify anything from the HashModel
    # or have something in commong for all subsequent models
    ...


class FunctionSaveModel(BaseHashModel):
    name: str

    serialized_function: bytes


class ParameterSaveModel(BaseHashModel):
    name: str
