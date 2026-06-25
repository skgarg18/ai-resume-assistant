from fastapi import APIRouter, HTTPException
from services.supabase_client import supabase

router = APIRouter()


@router.get("/api/session/{session_id}")
async def get_session_data(session_id: str):
    try:
        results = (
            supabase
            .table("resumes")
            .select("*")
            .eq("session_id", session_id)
            .order("score", desc=True)
            .execute()
        )

        if not results.data:
            raise HTTPException(
                status_code=404,
                detail="Session not found"
            )

        formatted_results = []

        for row in results.data:
            signed_url = (
                supabase.storage
                .from_("resume-files")
                .create_signed_url(
                    row["file_url"],
                    3600
                )
            )

            formatted_results.append({
                **row,
                "signed_file_url": signed_url["signedURL"]
            })

            # print(formatted_results)

        return {
            "results": formatted_results
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )