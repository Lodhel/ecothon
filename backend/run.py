from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from backend.app.routes import router


def create_app() -> FastAPI:
    app: FastAPI = FastAPI(title="MVP v.0.1", version="0.1.0", description='API MVP services.', redoc_url='/openapi')
    app.include_router(router)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


application: FastAPI = create_app()
