from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError

from auth.security import verify_token


# Extracts "Authorization: Bearer <token>"
security = HTTPBearer()


import logging

logger = logging.getLogger(__name__)

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Validate the JWT and return its payload.
    """

    token = credentials.credentials

    try:
        payload = verify_token(token)

        logger.debug(
            "JWT validated successfully | user_id=%s",
            payload.get("sub"),
        )

        return payload

    except JWTError:
        logger.warning(
            "Invalid or expired JWT received."
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    except Exception:
        logger.exception(
            "Unexpected error while validating JWT."
        )
        raise