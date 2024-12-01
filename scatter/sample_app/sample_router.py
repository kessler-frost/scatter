from fastapi.routing import APIRouter

router = APIRouter()


@router.get("/phased/route_1")
async def phased_route_1():
    return {"route_1": "response"}

@router.get("/phased/{route_name}")
async def phased_route_2(route_name: str):
    return {route_name: "response"}
