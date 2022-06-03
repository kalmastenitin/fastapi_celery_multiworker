
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles


import os
import sys


def create_app():
    app = FastAPI(
        title="Test Celery",
        description="Make Own Queues",
        version="0.0.1",
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    from .routes import router as service_router
    app.include_router(service_router, prefix="/api")
    return app


app = create_app()
