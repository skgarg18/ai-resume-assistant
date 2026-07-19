from fastapi import APIRouter, HTTPException
from database.active_repository import resume_repo, files_repo

router = APIRouter()


@router.get("/api/session/{session_id}")
async def get_session_data(session_id: str):
    try:

        results = resume_repo.get_resume_data_ordered_by_score(session_id)

        if not results:
            raise HTTPException(
                status_code=404,
                detail="Session not found"
            )

        formatted_results = []

        for row in results:
            signed_url = (

                files_repo.get_signed_url(
                    row["file_url"]
                )
            )

            formatted_results.append({
                **row,
                "signed_file_url": signed_url
            })

            # print(formatted_results)

        return {
            "results": formatted_results
        }

    except HTTPException:
        raise

    except Exception as e:
        print(f"Error fetching data for {session_id}: {e}\n")

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )