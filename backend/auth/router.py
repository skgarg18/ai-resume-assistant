import logging
from time import perf_counter

logger = logging.getLogger(__name__)


import os

# from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, status

from auth.schemas import LoginRequest, TokenResponse
from auth.security import create_access_token, verify_password

from database.active_repository import user_repo

# load_dotenv()

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


# ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
# ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    request: LoginRequest,
):
    """
    Authenticate the user and return a JWT.
    """

    start_time = perf_counter()

    try:
        logger.info(
            "Login attempt for email: %s",
            request.email,
        )

        user = user_repo.get_user_by_email(request.email)

        if (
            user is None
            or not verify_password(
                request.password,
                user.password_hash,
            )
        ):
            logger.warning(
                "Failed login attempt for email: %s (Invalid credentials)",
                request.email,
            )

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not user.is_active:
            logger.warning(
                "Login blocked for inactive user: %s",
                request.email,
            )

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive.",
            )

        access_token = create_access_token(
            {
                "sub": str(user.id),
            }
        )

        logger.info(
            "User logged in successfully: %s (%.3f sec)",
            request.email,
            perf_counter() - start_time,
        )

        return TokenResponse(
            access_token=access_token,
        )

    except HTTPException:
        raise

    except Exception:
        logger.exception(
            "Unexpected error during login for email: %s",
            request.email,
        )
        raise