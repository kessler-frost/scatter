from fastapi import FastAPI
from fastapi.routing import APIRoute
import scatter
from contextlib import asynccontextmanager
import os
from scatter.sample_app.sample_router import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    scatter.init(redis_url=os.getenv("REDIS_URL"))
    for route in app.routes:
        if isinstance(route, APIRoute):
            print(f"Path: {route.path}, Name: {route.name}, Methods: {route.methods}, Endpoint: {route.endpoint}")
    yield
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
