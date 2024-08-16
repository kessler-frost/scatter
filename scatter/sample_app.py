from fastapi import FastAPI
import scatter
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    scatter.init()
    yield
    scatter.shutdown()


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def read_root():
    sample_task = scatter.assemble("sample_task")
    return {
        "source": sample_task.source,
        "res": sample_task()
    }
