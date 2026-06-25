from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from services.google_oauth_service import oauth
from services.supabase_client import supabase

router = APIRouter()

oauth_store = {}

@router.get("/auth/google")
async def google_login(request: Request):

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

    token = await oauth.google.authorize_access_token(
        request
    )

    userinfo = await oauth.google.userinfo(
        token=token
    )

    print(userinfo)

    print(token)

    refresh_token = token.get(
    "refresh_token"
    )

    google_email = userinfo["email"]

    supabase.table(
        "google_integrations"
    ).upsert({
        "user_id" : 1,
        "google_email": google_email,
        "refresh_token": refresh_token
    }).execute()

    return RedirectResponse(
        url=(
            "http://localhost:3000"
            "?google_connected=true"
            f"&email={userinfo['email']}"
        )
    )