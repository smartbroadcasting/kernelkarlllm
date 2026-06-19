from fastapi import APIRouter, Request

router = APIRouter(tags=["models"])


@router.get("/models")
async def models(request: Request) -> dict:
    return request.app.state.backend.model_info()
