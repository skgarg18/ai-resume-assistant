from logs.log_context import get_logger, set_logger
from logs.logging_config import logger as base_logger
from time import perf_counter

from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import RedirectResponse

from services.google_oauth_service import oauth
from database.active_repository import google_user_repo

router = APIRouter()


@router.get("/auth/google")
async def google_login(
    request: Request,
    ):

    logger = get_logger()



    logger.info("Initiating Google OAuth login")

    redirect_uri = (
        "http://localhost:8000/auth/google/callback"
    )

    return await oauth.google.authorize_redirect(
        request,
        redirect_uri,
        access_type="offline",
        prompt="consent"
    )


@router.get("/auth/google/callback")
async def google_callback(request: Request):

    start = perf_counter()

    logger = get_logger()

    logger.info("Received Google OAuth callback")

    try:

        logger.info("Exchanging authorization code for access token")

        token = await oauth.google.authorize_access_token(request)

        logger.info("Fetching Google user information")

        userinfo = await oauth.google.userinfo(token=token)

        refresh_token = token.get("refresh_token")

        google_id = userinfo["sub"]
        email = userinfo["email"]
        name = userinfo["name"]
        picture = userinfo.get("picture")

        logger.info(
            "Upserting Google user | google_id={} | email={}",
            google_id,
            email,
        )

        upsert_result = google_user_repo.update_or_insert_user_data(
            google_id=google_id,
            email=email,
            name=name,
            picture=picture,
            refresh_token=refresh_token
        )

        if upsert_result is None:

            logger.error(
                "Failed to upsert Google user | google_id={}",
                google_id,
            )

            raise HTTPException(
                    status_code=500,
                    detail="Failed to upsert user data"
                    )


        logger.info(
            "Fetching internal user ID | google_id={}",
            google_id,
        )

        # Fetch the generated internal user_id

        result = google_user_repo.get_user_data_by_google_id(google_id=google_id)

        if result is None:

            logger.error(
                "Failed to retrieve user after upsert | google_id={}",
                google_id,
            )

            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve user data",
            )

        user_id = result["user_id"]

        logger.info(
            "Google OAuth completed successfully | user_id={} | duration={:.2f}s",
            user_id,
            perf_counter() - start,
        )


        return RedirectResponse(
            url=(
                f"http://localhost:3000"
                f"?google_connected=true"
                f"&user_id={user_id}"
            )
        )
    
    except HTTPException:
        raise

    except Exception:

        logger.exception(
            "Unexpected error during Google OAuth callback"
        )

        raise HTTPException(
            status_code=500,
            detail="Google authentication failed",
        )