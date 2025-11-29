from fastapi import APIRouter

router = APIRouter()


@router.get("/", summary="List users")
def list_users():
    return {"users": []}
