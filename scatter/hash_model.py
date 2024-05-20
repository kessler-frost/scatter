from redis_om import HashModel, Field


class Function(HashModel):
    name: str = Field(default=None, primary_key=True)
    callable_: str
