import os # PyMuPDF
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import json

from routers.chat_router.chat_router import router as chat
from routers.upload_files_router import router as upload_and_screen
from routers.retrive_data import router as  get_session_data
from routers.chatHistory_router import router as chat_history
from routers.retrive_sessions_router import router as retrive_sessions
from routers.regenerate_email_content_router import router as regenerate_email
from routers.send_email_router import router as send_email_router
from routers.google_oauth_router import router as google_auth_router
from routers.delete_session_data_router import router as delete_session_data_router
from routers.export_excel_router import router as export_excel_router

from auth.router import router as auth_router

from utils.log_utils import set_logger, reset_logger, default_logger, get_logger

from services.embedding_model import get_embedding_model
from services.reranker_model import get_reranker_model


logger = get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This runs BEFORE the app starts accepting requests
    logger.info("Pre-loading ML models into memory on application startup...")
    get_embedding_model()
    get_reranker_model()
    logger.info("All ML models pre-loaded and warm in RAM!")
    
    yield  # FastAPI handles HTTP requests while yielded
    
    # Optional cleanup on shutdown


app = FastAPI(lifespan=lifespan)

# Allow Next.js frontend to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    # Reset to base clean logger per request
    token = set_logger(default_logger)
    try:
        response = await call_next(request)
        return response
    finally:
        reset_logger(token)




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
    auth_router,
    tags=["login"])

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

app.include_router(
    export_excel_router,
    prefix="/api/session",
    tags=["export_excel_router"]
)