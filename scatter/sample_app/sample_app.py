from fastapi import FastAPI
import scatter
from contextlib import asynccontextmanager
import os
from scatter.sample_app.sample_router import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    scatter.init(redis_url=os.getenv("REDIS_URL"))

    yield

    # Delete everything when exiting
    scatter.main.__flushall()
    scatter.cleanup()


app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/integration")
async def fastapi_integration():
    return {"gigachad": 42}

app.include_router(router)
app = scatter.integrate_app(app)
