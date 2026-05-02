"""FastAPI server exposing the compliance audit pipeline as a REST API."""

import uuid
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

from dotenv import load_dotenv
load_dotenv(override=True)

from backend.src.api.telemetry import setup_telemetry
setup_telemetry()

from backend.src.graph.workflow import app as compliance_graph

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("audit-agent-api")

app = FastAPI(
    title="Audit Agent API",
    description="Audits video content against brand compliance rules.",
    version="1.0.0"
)


class AuditRequest(BaseModel):
    """Incoming request payload."""
    video_url: str


class ComplianceIssue(BaseModel):
    """Single compliance violation."""
    category: str
    severity: str
    description: str


class AuditResponse(BaseModel):
    """Audit result returned to the client."""
    session_id: str
    video_id: str
    status: str
    final_report: str
    compliance_results: List[ComplianceIssue]


@app.post("/audit", response_model=AuditResponse)
async def audit_video(request: AuditRequest):
    """Triggers the compliance audit workflow for a given video URL."""
    session_id = str(uuid.uuid4())
    video_id_short = f"vid_{session_id[:8]}"

    logger.info(f"Audit request received: {request.video_url} (session: {session_id})")

    initial_inputs = {
        "video_url": request.video_url,
        "video_id": video_id_short,
        "compliance_results": [],
        "errors": []
    }

    try:
        final_state = compliance_graph.invoke(initial_inputs)

        return AuditResponse(
            session_id=session_id,
            video_id=final_state.get("video_id"),
            status=final_state.get("final_status", "UNKNOWN"),
            final_report=final_state.get("final_report", "No report generated."),
            compliance_results=final_state.get("compliance_results", [])
        )

    except Exception as e:
        logger.error(f"Audit failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Workflow execution failed: {str(e)}"
        )


@app.get("/health")
def health_check():
    """Returns API health status."""
    return {"status": "healthy", "service": "Audit Agent"}