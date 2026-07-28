from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from config.constants import LOG_DIR
from utils.log_utils import get_logger

LOG_FILE = LOG_DIR / "llm_usage.jsonl"

LOG_FILE.parent.mkdir(parents=True, exist_ok=True)


def extract_token_usage(response: Any) -> dict[str, int]:
    """
    Extract token usage from a LangChain AIMessage.

    Supports:
    - ChatGroq (LangChain)
    - OpenAI (LangChain)
    - Other providers exposing token usage in response_metadata
    """

    usage = {}

    if hasattr(response, "usage_metadata") and response.usage_metadata:
        usage = response.usage_metadata

    elif hasattr(response, "response_metadata"):
        usage = response.response_metadata.get("token_usage", {})

    return {
        "input_tokens": (
            usage.get("input_tokens")
            or usage.get("prompt_tokens")
            or 0
        ),
        "output_tokens": (
            usage.get("output_tokens")
            or usage.get("completion_tokens")
            or 0
        ),
        "total_tokens": usage.get("total_tokens", 0),
    }


def _write_usage_record(record: dict):
    """
    Writes usage record to llm_usage.jsonl.
    """

    logger = get_logger()

    try:
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record))
            f.write("\n")

    except Exception:
        logger.exception(
            "Failed to write LLM usage log."
        )


def _log_usage(
    *,
    operation: str,
    model: str,
    session_id: str | None,
    input_tokens: int,
    output_tokens: int,
    total_tokens: int,
    latency_ms: float,
    success: bool,
    error: str | None,
):
    """
    Common logging function for all LLM providers.
    """

    logger = get_logger()

    record = {
        "timestamp": datetime.now(
            ZoneInfo("Asia/Kolkata")
        ).isoformat(),
        "operation": operation,
        "model": model,
        "session_id": session_id,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "latency_ms": round(latency_ms, 2),
        "success": success,
        "error": error,
    }

    if success:

        logger.info(
            "LLM call completed | "
            "operation={} | "
            "model={} | "
            "input_tokens={} | "
            "output_tokens={} | "
            "total_tokens={} | "
            "latency_ms={:.2f}",
            operation,
            model,
            input_tokens,
            output_tokens,
            total_tokens,
            latency_ms,
        )

    else:

        logger.error(
            "LLM call failed | "
            "operation={} | "
            "model={} | "
            "latency_ms={:.2f} | "
            "error={}",
            operation,
            model,
            latency_ms,
            error,
        )

    _write_usage_record(record)


def log_llm_usage(
    *,
    operation: str,
    response: Any,
    latency_ms: float,
    model: str | None = None,
    session_id: str | None = None,
    success: bool = True,
    error: str | None = None,
):
    """
    Log usage for LangChain responses.
    """

    usage = extract_token_usage(response)

    if model is None:
        response_metadata = getattr(
            response,
            "response_metadata",
            {},
        )
        model = response_metadata.get(
            "model_name",
            "unknown",
        )

    _log_usage(
        operation=operation,
        model=model,
        session_id=session_id,
        input_tokens=usage["input_tokens"],
        output_tokens=usage["output_tokens"],
        total_tokens=usage["total_tokens"],
        latency_ms=latency_ms,
        success=success,
        error=error,
    )


def log_groq_usage(
    *,
    operation: str,
    response,
    latency_ms: float,
    session_id: str | None = None,
    success: bool = True,
    error: str | None = None,
):
    """
    Log usage for official Groq SDK responses.
    """

    usage = getattr(response, "usage", None)

    _log_usage(
        operation=operation,
        model=getattr(response, "model", "unknown"),
        session_id=session_id,
        input_tokens=usage.prompt_tokens if usage else 0,
        output_tokens=usage.completion_tokens if usage else 0,
        total_tokens=usage.total_tokens if usage else 0,
        latency_ms=latency_ms,
        success=success,
        error=error,
    )