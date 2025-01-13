from fastapi.routing import APIRouter

router = APIRouter()


@router.get("/phased/route_1")
async def phased_route_1():
    return {"route_1": "response"}

@router.get("/phased/{route_name}")
async def phased_route_2(route_name: str):
    return {route_name: "my name is!"}

async def not_an_endpoint():
    return "I'm not an endasdasdt!"
