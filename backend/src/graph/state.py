"""State schema for the video compliance audit pipeline."""

import operator
from typing import Annotated, List, Dict, Optional, Any, TypedDict


class ComplianceIssue(TypedDict):
    """Represents a single compliance violation found during video audit."""
    category: str            # e.g., "FTC_DISCLOSURE"
    description: str         # Detail of the violation
    severity: str            # "CRITICAL" | "WARNING"
    timestamp: Optional[str] # Occurrence timestamp if available


class VideoAuditState(TypedDict):
    """LangGraph state schema shared across all pipeline nodes."""

    # --- Input ---
    video_url: str
    video_id: str

    # --- Ingestion ---
    local_file_path: Optional[str]
    video_metadata: Dict[str, Any]
    transcript: Optional[str]
    ocr_text: List[str]

    # --- Analysis ---
    # operator.add enables append-only updates across nodes
    compliance_results: Annotated[List[ComplianceIssue], operator.add]

    # --- Output ---
    final_status: str   # "PASS" | "FAIL"
    final_report: str   # Markdown summary

    # --- System ---
    # Appends errors without halting execution
    errors: Annotated[List[str], operator.add]