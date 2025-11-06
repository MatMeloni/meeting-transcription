from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.controller.pipeline_controller import PipelineController
from backend.api.routes import build_router


def create_app(controller: PipelineController) -> FastAPI:
    """Initializes the FastAPI application with routes and middleware."""
    app = FastAPI(
        title="Meeting Transcription API",
        version="1.0.0",
        description="Controle da API para o pipeline de transcrição e resumo automático.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    router = build_router(controller)
    app.include_router(router)
    return app
