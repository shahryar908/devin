import socketio
from sqlalchemy.orm import Session

from db import User, engine
from security import decode_token
from ws.game import DIFFICULTIES
from ws.room_manager import manager

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
manager.bind_sio(sio)


async def _who(sid) -> tuple[int, str]:
    session = await sio.get_session(sid)
    return (session["user_id"], session["username"])


@sio.event
async def connect(sid, environ, auth):
    token = (auth or {}).get("token")
    if not token:
        return False
    try:
        payload = decode_token(token)
    except Exception:
        return False
    if payload.get("type") != "access":
        return False
    with Session(engine) as session:
        user = session.get(User, int(payload["sub"]))
    if user is None:
        return False
    await sio.save_session(sid, {"user_id": user.id, "username": user.username})
    return True


@sio.event
async def disconnect(sid):
    await manager.leave(sid)


@sio.on("room:create")
async def on_room_create(sid, data):
    user_id, username = await _who(sid)
    data = data or {}
    mode = data.get("mode", "blitz") or "blitz"
    duration = int(data.get("duration", 60) or 60)
    difficulty = data.get("difficulty", "medium") or "medium"
    if difficulty not in DIFFICULTIES:
        difficulty = "medium"
    try:
        await manager.create(sid, user_id, username, mode, duration, difficulty)
    except ValueError as e:
        await sio.emit("room:error", {"message": str(e)}, to=sid)


@sio.on("room:join")
async def on_room_join(sid, data):
    user_id, username = await _who(sid)
    data = data or {}
    code = str(data.get("code", "")).strip().upper()
    room = manager.get(code)
    if room is None:
        await sio.emit("room:error", {"message": "Room not found"}, to=sid)
        return
    if room.state != "lobby":
        await sio.emit("room:error", {"message": "Room already started"}, to=sid)
        return
    if len(room.players) >= 2:
        await sio.emit("room:error", {"message": "Room is full"}, to=sid)
        return
    try:
        await manager.join(room, sid, user_id, username)
    except ValueError as e:
        await sio.emit("room:error", {"message": str(e)}, to=sid)


@sio.on("room:leave")
async def on_room_leave(sid, data=None):
    await manager.leave(sid)


@sio.on("match:requestStart")
async def on_request_start(sid, data=None):
    try:
        await manager.request_start(sid)
    except ValueError as e:
        await sio.emit("room:error", {"message": str(e)}, to=sid)


@sio.on("answer:submit")
async def on_answer(sid, data):
    data = data or {}
    question_id = str(data.get("questionId", ""))
    try:
        answer = int(data.get("answer"))
    except (TypeError, ValueError):
        return
    await manager.submit_answer(sid, question_id, answer)