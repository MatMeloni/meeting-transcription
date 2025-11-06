from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from backend.controller.pipeline_controller import PipelineController
from backend.model import PipelineResponseSchema


def build_router(controller: PipelineController) -> APIRouter:
    """Creates an APIRouter with endpoints bound to the controller."""
    router = APIRouter()

    @router.get("/health")
    async def health() -> dict[str, str]:
        """Simple health check endpoint."""
        return {"status": "ok"}

    @router.post("/transcribe")
    async def transcribe_endpoint(
        file: UploadFile = File(...),
        meeting_name: Optional[str] = None,
    ) -> JSONResponse:
        """Accepts an audio upload, processes it, and returns transcript plus summary."""
        meeting_label = meeting_name or controller.config.default_meeting_name
        payload = await file.read()
        if not payload:
            raise HTTPException(status_code=400, detail="Arquivo de áudio vazio.")
        result = controller.process_uploaded_bytes(
            payload=payload,
            original_filename=file.filename or "upload.wav",
            meeting_name=meeting_label,
            export_results=True,
        )
        schema = PipelineResponseSchema.from_result(result)
        return JSONResponse(schema.model_dump())

    return router
