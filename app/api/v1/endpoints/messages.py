from fastapi import APIRouter

router = APIRouter()


@router.get("/", summary="List messages")
def list_messages():
    return {"messages": []}
