"""
Service for generating Zoom meeting links.
"""

import os

import requests
from requests.auth import HTTPBasicAuth

from utils.log_utils import get_logger


def get_zoom_access_token() -> str:
    """
    Authenticate with Zoom and return an access token.
    """

    logger = get_logger()

    account_id = os.getenv("ZOOM_ACCOUNT_ID")
    client_id = os.getenv("ZOOM_CLIENT_ID")
    client_secret = os.getenv("ZOOM_CLIENT_SECRET")

    token_url = (
        "https://zoom.us/oauth/token"
        f"?grant_type=account_credentials"
        f"&account_id={account_id}"
    )

    try:

        response = requests.post(
            token_url,
            auth=HTTPBasicAuth(
                client_id,
                client_secret,
            ),
            timeout=30,
        )

        response.raise_for_status()

        logger.info("Successfully authenticated with Zoom")

        return response.json()["access_token"]

    except Exception:

        logger.exception(
            "Failed to authenticate with Zoom"
        )

        raise


def generate_zoom_link(
    candidate_name: str,
    start_time_iso: str,
) -> str:
    """
    Create a Zoom meeting and return the meeting join URL.
    """

    logger = get_logger()

    try:

        logger.info(
            "Creating Zoom meeting | candidate={}",
            candidate_name,
        )

        token = get_zoom_access_token()

        meeting_url = (
            "https://api.zoom.us/v2/users/me/meetings"
        )

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        payload = {
            "topic": f"Interview: {candidate_name}",
            "type": 2,
            "start_time": start_time_iso,
            "timezone": "Asia/Kolkata",
            "settings": {
                "host_video": True,
                "participant_video": True,
                "join_before_host": False,
                "waiting_room": True,
            },
        }

        response = requests.post(
            meeting_url,
            headers=headers,
            json=payload,
            timeout=30,
        )

        response.raise_for_status()

        meeting_data = response.json()

        logger.info(
            "Zoom meeting created successfully | meeting_id={}",
            meeting_data.get("id"),
        )

        return meeting_data["join_url"]

    except requests.HTTPError:

        logger.exception(
            "Zoom API returned an error while creating meeting"
        )

    except Exception:

        logger.exception(
            "Failed to create Zoom meeting"
        )

    return "https://zoom.us/error-generating-link"