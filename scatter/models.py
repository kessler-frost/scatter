from pydantic import BaseModel
from redis.client import Pipeline


# NOTE: Potential models for later to facilitate storage

class CustomBaseModel(BaseModel):
    pipeline: Pipeline


class VersionedFunction(CustomBaseModel):
    version: int
    source: str


class Function(CustomBaseModel):
    name: str
    latest: int
