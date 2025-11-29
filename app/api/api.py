from fastapi import FastAPI

from .v1.endpoints import user, messages, auth, community


def create_app() -> FastAPI:
    app = FastAPI(title="Mona360 Community Chat API")
    # v1 routes
    app.include_router(user, prefix="/v1/users", tags=["users"])
    app.include_router(messages, prefix="/v1/messages", tags=["messages"])
    app.include_router(auth, prefix="/v1/auth", tags=["auth"])
    app.include_router(community, prefix="/v1/communities", tags=["communities"])
    return app


app = create_app()
