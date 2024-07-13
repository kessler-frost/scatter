from redis_om import JsonModel, Field
from typing import Dict


class VersionedFunction(JsonModel):
    version: int
    source: str


class Function(JsonModel):
    name: str = Field(index=True)
    latest: int
    versioned_functions: Dict[int, VersionedFunction]
