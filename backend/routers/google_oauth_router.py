from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from services.google_oauth_service import oauth
from services.supabase_client import supabase

router = APIRouter()


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

    token = await oauth.google.authorize_access_token(request)

    userinfo = await oauth.google.userinfo(token=token)

    refresh_token = token.get("refresh_token")

    google_id = userinfo["sub"]
    email = userinfo["email"]
    name = userinfo["name"]
    picture = userinfo.get("picture")

    # Upsert user based on unique google_id
    supabase.table("users").upsert(
        {
            "google_id": google_id,
            "email": email,
            "name": name,
            "picture": picture,
            "refresh_token": refresh_token,
        },
        on_conflict="google_id",
    ).execute()

    # Fetch the generated internal user_id
    result = (
        supabase.table("users")
        .select("user_id")
        .eq("google_id", google_id)
        .single()
        .execute()
    )

    user_id = result.data["user_id"]

    return RedirectResponse(
        url=(
            f"http://localhost:3000"
            f"?google_connected=true"
            f"&user_id={user_id}"
        )
    )