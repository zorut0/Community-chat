from fastapi import APIRouter

router = APIRouter()


@router.get("/", summary="List communities")
def list_communities():
    return {"communities": []}
