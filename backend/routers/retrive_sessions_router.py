from fastapi import APIRouter, HTTPException
from database.active_repository import session_repo

router = APIRouter()

@router.get("/api/sessions")
async def get_sessions():

    try:

        # print("Deriving Sessions\n")

        response = session_repo.get_sessions()

        # print("Response\n")
        # print(response)


        if response is None:
            raise HTTPException(
                status_code=404,
                detail="Error fetching sessions"
            )

        return response
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )