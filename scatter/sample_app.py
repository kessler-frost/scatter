from fastapi import FastAPI
import scatter
from contextlib import asynccontextmanager
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    scatter.init(redis_url=os.getenv("RAILWAY_REDIS"))
    yield
    scatter.cleanup()


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def read_root():
    sample_task = scatter.get("sample_task_1")
    return {"source": sample_task.source, "res": sample_task(4, 2)}


# from fastapi import FastAPI
# import inspect

# app = FastAPI()


# def sample_task():
#     return 42
# sample_task.source = inspect.getsource(sample_task)

# @app.get("/")
# async def read_root():
#     return {
#         "source": sample_task.source,
#         "res": sample_task()
#     }
