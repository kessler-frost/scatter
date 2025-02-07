from fastapi import FastAPI
import scatter
from sample_router import router

app = FastAPI()

@app.get("/")
def read_root():
    return {"Arthur": "Dent"}


@app.get("/integration")
async def fastapi_integration():
    return {"Dirk Gently": 42}

app.include_router(router)

app = scatter.integrate_app(app)
