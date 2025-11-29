from fastapi import APIRouter

router = APIRouter()


@router.get("/", summary="Auth ping")
def auth_ping():
    return {"auth": "ok"}
