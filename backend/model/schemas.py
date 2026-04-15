from __future__ import annotations

from typing import Any, Dict, List

from pydantic import BaseModel


class SegmentSchema(BaseModel):
    """Represents a single transcript segment."""

    id: int
    start: float
    end: float
    text: str


class SemanticClusterSchema(BaseModel):
    """Represents a semantic cluster aggregated from segments."""

    label: str
    start_time: float
    end_time: float
    text: str


class SummarySchema(BaseModel):
    """Structured meeting summary sections."""

    decisions: List[str] = []
    pending: List[str] = []
    next_steps: List[str] = []
    overview: List[str] = []

    class Config:
        extra = "allow"


class PipelineResponseSchema(BaseModel):
    """Full payload returned to clients after running the pipeline."""

    meeting_name: str
    timestamp: str
    transcript_text: str
    segments: List[SegmentSchema]
    semantic_clusters: List[SemanticClusterSchema]
    summary: SummarySchema
    exports: Dict[str, Dict[str, str]] = {}
    stage_timings: Dict[str, float] = {}

    @classmethod
    def from_result(cls, result: Dict[str, Any]) -> "PipelineResponseSchema":
        """Factory that normalizes the raw pipeline dictionary."""
        summary_data = result.get("summary", {})
        summary = SummarySchema(**summary_data)
        payload = {
            "meeting_name": result["meeting_name"],
            "timestamp": result["timestamp"],
            "transcript_text": result["transcript_text"],
            "segments": result.get("segments", []),
            "semantic_clusters": result.get("semantic_clusters", []),
            "summary": summary,
            "exports": result.get("exports", {}),
            "stage_timings": result.get("stage_timings", {}),
        }
        return cls(**payload)
