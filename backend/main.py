import os # PyMuPDF
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


import json

from routers.chat_router import router as chat
from routers.generate_question_router import router as generate_questions
from routers.upload_files_router import router as upload_and_screen



app = FastAPI()

# Allow Next.js frontend to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    upload_and_screen,
    tags = ["upload_and_screen"]
)

app.include_router(
    generate_questions,
    tags = ["generate_questions"]
)

app.include_router(
    chat,
    tags = ["chat"]
)


















