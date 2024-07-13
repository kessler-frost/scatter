import warnings
warnings.filterwarnings("ignore", category=UserWarning)

from redis_om import JsonModel, Field


class FunctionMetadataModel(JsonModel):
    name: str = Field(index=True)
