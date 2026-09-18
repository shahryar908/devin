from fastapi import APIRouter, HTTPException

from ws.room_manager import manager

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.get("/{code}")
def get_room(code: str) -> dict:
    room = manager.get(code.strip().upper())
    if room is None:
        raise HTTPException(404, "Room not found")
    return room.info()