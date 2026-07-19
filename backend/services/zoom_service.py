# services/zoom_service.py
import os
import requests
from requests.auth import HTTPBasicAuth
from dateutil import parser

def get_zoom_access_token() -> str:
    """Authenticates with Zoom and returns a temporary bearer token."""
    account_id = os.getenv("ZOOM_ACCOUNT_ID")
    client_id = os.getenv("ZOOM_CLIENT_ID")
    client_secret = os.getenv("ZOOM_CLIENT_SECRET")

    token_url = f"https://zoom.us/oauth/token?grant_type=account_credentials&account_id={account_id}"
    
    response = requests.post(
        token_url, 
        auth=HTTPBasicAuth(client_id, client_secret)
    )
    
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        raise Exception(f"Failed to get Zoom token: {response.text}")

import requests


def generate_zoom_link(
    candidate_name: str,
    start_time_iso: str
) -> str:
    """
    Creates a scheduled Zoom meeting and
    returns the join URL.
    """

    try:
        # Get Zoom access token
        token = get_zoom_access_token()

        # Zoom create meeting endpoint
        meeting_url = "https://api.zoom.us/v2/users/me/meetings"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
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
                "waiting_room": True
            }
        }

        response = requests.post(
            meeting_url,
            headers=headers,
            json=payload
        )

        if response.status_code == 201:
            meeting_data = response.json()

            # print(
            #     f"Zoom meeting created successfully: "
            #     f"{meeting_data}"
            # )

            return meeting_data.get("join_url")

        print(f"Zoom Error: {response.text}")
        return "https://zoom.us/error-generating-link"

    except Exception as e:
        print(f"Failed to create Zoom meeting: {e}")
        return "https://zoom.us/error-generating-link"