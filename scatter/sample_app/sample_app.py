from fastapi import FastAPI
from fastapi.routing import APIRoute
import scatter
from contextlib import asynccontextmanager
import os
from scatter.sample_app.sample_router import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    for route in app.routes:
        if isinstance(route, APIRoute):
            print(f"Path: {route.path}, Name: {route.name}, Methods: {route.methods}, Endpoint: {route.endpoint}")
    yield
    scatter.cleanup()


app = FastAPI(lifespan=lifespan)

@app.get("/")
async def read_root():
    # sample_task = scatter.get("sample_task_1")
    # return {"source": sample_task.source, "res": sample_task(4, 2)}
    return {"Hello": "World"}

@app.get("/integration")
async def fastapi_integration():
    return {"gigachad": 42}


app.include_router(router)

# Integrate scatter with the FastAPI app
scatter.init(redis_url=os.getenv("REDIS_URL"))
app = scatter.integrate_app(app)

