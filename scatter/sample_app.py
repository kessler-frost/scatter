from fastapi import FastAPI
import scatter
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    scatter.init()
    yield
    scatter.cleanup()


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def read_root():
    sample_task = scatter.get("sample_task")
    return {
        "source": sample_task.source,
        "res": sample_task()
    }
