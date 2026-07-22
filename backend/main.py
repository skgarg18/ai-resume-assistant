import os # PyMuPDF
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


import json

from logs import logging_config

from routers.chat_router.chat_router import router as chat
from routers.upload_file_router.upload_files_router import router as upload_and_screen
from routers.retrive_data import router as  get_session_data
from routers.chatHistory_router import router as chat_history
from routers.retrive_sessions_router import router as retrive_sessions
from routers.chat_router.regenerate_email_content_router import router as regenerate_email
from routers.send_email_router import router as send_email_router
from routers.google_oauth_router import router as google_auth_router
from routers.delete_session_data_router import router as delete_session_data_router


app = FastAPI()

# Allow Next.js frontend to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


from fastapi.staticfiles import StaticFiles

app.mount(
    "/files",
    StaticFiles(directory="database/dbtype/local_storage/files"),
    name="files",
)


from starlette.middleware.sessions import SessionMiddleware

app.add_middleware(
    SessionMiddleware,
    secret_key="some-random-secret-key"
)


app.include_router(
    upload_and_screen,
    tags = ["upload_and_screen"]
)

app.include_router(
    chat,
    tags = ["chat"]
)

app.include_router(
    get_session_data,
    tags=["get_session_data"]
)

app.include_router(
    chat_history,
    tags=['chat_history']
)

app.include_router(
    retrive_sessions,
    tags=['retrive_sessions']
)

app.include_router(
    regenerate_email,
    tags=['regenerate_email']
)


app.include_router(
    send_email_router,
    tags=['send_enail']
)

app.include_router(
    google_auth_router,
    tags=['google_auth']
)

app.include_router(
    delete_session_data_router,
    tags=['delete_session_data']
)