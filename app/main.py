from fastapi import FastAPI
from routers import audio, user

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.include_router(audio.router)
app.include_router(user.router)


origins = [
    "*", # Allow all origins UNSECURE
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)