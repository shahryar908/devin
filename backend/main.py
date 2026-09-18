import socketio
from fastapi import FastAPI

from routes.auth.auth import router as auth_router
from routes.leaderboard.leaderboard import router as leaderboard_router
from routes.rooms.rooms import router as rooms_router
from ws.server import sio  # noqa: F401  (registers socket.io handlers)
from ws.room_manager import manager

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Math Duel Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(rooms_router)
app.include_router(leaderboard_router)

manager.bind_sio(sio)

sio_app = socketio.ASGIApp(sio, other_asgi_app=app)