import urllib.parse
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse

from utils.log_utils import bind_logger

from database.active_repository import (
    session_repo,
    resume_repo
)
from utils.excel_report import ExcelReportGenerator
from auth.dependencies import get_current_user

router = APIRouter()

@router.get("/{session_id}/export", response_class=StreamingResponse)
def export_session_report(
    session_id: str,
    current_user = Depends(get_current_user)
):
    """
    Generates and streams a custom executive Excel evaluation report completely in memory.
    """
    logger = bind_logger(session_id = session_id)

    logger.info(f"Report generation started for session_id: {session_id}")

    try:


        # 1. Fetch & Validate Session
        session_data = session_repo.get_session_data_by_session_id(session_id)

        if not session_data:
            logger.warning(f"Session not found: {session_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session with ID '{session_id}' was not found."
            )
        logger.info(f"Session fetched successfully for ID: {session_id}")

        # 2. Fetch Candidates Data
        candidates_data = resume_repo.get_resume_data(session_id)
        candidate_count = len(candidates_data)
        logger.info(f"Retrieved candidate records. Count: {candidate_count}")

        if candidate_count == 0:
            logger.warning(f"No candidate evaluations exist for session: {session_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot generate report. No candidate evaluations found for this session."
            )

        # 3. Generate Workbook in Memory
        generator = ExcelReportGenerator(session_data, candidates_data)
        excel_buffer = generator.generate()
        
        buffer_size = excel_buffer.getbuffer().nbytes
        logger.info(f"Workbook generated successfully. Size: {buffer_size} bytes")

        # 4. Construct Content-Disposition Header (RFC 5987 compliant)
        filename = f"Resume_Evaluation_Report_{session_id}.xlsx"
        encoded_filename = urllib.parse.quote(filename)

        # 5. Return StreamingResponse directly from BytesIO
        headers = {
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}",
            "Access-Control-Expose-Headers": "Content-Disposition"
        }

        logger.info(f"Report download completed initiating stream for session: {session_id}")
        return StreamingResponse(
            excel_buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers=headers
        )

    except HTTPException as http_exc:
        raise http_exc
    except Exception as exc:
        logger.exception(f"Unhandled exception during report generation for session {session_id}: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while generating the Excel evaluation report."
        )