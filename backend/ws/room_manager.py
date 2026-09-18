import asyncio
from datetime import datetime, timedelta, timezone

from ws.game import generate_question, room_code

POINTS_PER_CORRECT = 10
COUNTDOWN_SECONDS = 5
ANSWER_TIMEOUT = 3
ROOM_TTL_SECONDS = 60

from services.match import save_match


def utcnow():
    return datetime.now(timezone.utc)


class Player:
    def __init__(self, sid: str, user_id: int, username: str):
        self.sid = sid
        self.user_id = user_id
        self.username = username
        self.score = 0
        self.correct = 0
        self.total = 0
        self.question = None
        self.pending = None
        self.answered = asyncio.Event()

    def public(self) -> dict:
        return {
            "playerId": self.user_id,
            "username": self.username,
            "score": self.score,
        }


class Room:
    def __init__(self, code: str, host_id: int, mode: str, duration: int, difficulty: str):
        self.code = code
        self.host_id = host_id
        self.mode = mode
        self.duration = duration
        self.difficulty = difficulty
        self.state = "lobby"  # lobby | starting | playing | ended
        self.players: dict[str, Player] = {}
        self.ends_at: datetime | None = None
        self.started_at: datetime | None = None
        self.used = set()
        self._qid = [0]
        self._tasks: list[asyncio.Task] = []

    @property
    def by_user_id(self) -> dict[int, Player]:
        return {p.user_id: p for p in self.players.values()}

    def info(self) -> dict:
        return {
            "code": self.code,
            "mode": self.mode,
            "duration": self.duration,
            "difficulty": self.difficulty,
            "state": self.state,
            "hostId": self.host_id,
            "players": [p.public() for p in self.players.values()],
        }

    def _cancel_tasks(self):
        current = asyncio.current_task()
        remaining = []
        for t in self._tasks:
            if t is current:
                remaining.append(t)
                continue
            t.cancel()
        self._tasks = remaining


class RoomManager:
    def __init__(self):
        self.sio = None
        self.rooms: dict[str, Room] = {}
        self.sid_to_room: dict[str, Room] = {}

    def bind_sio(self, sio):
        self.sio = sio

    def room_by_sid(self, sid: str) -> Room | None:
        return self.sid_to_room.get(sid)

    def get(self, code: str) -> Room | None:
        return self.rooms.get(code)

    async def create(self, sid: str, user_id: int, username: str, mode: str, duration: int, difficulty: str) -> Room:
        room = None
        while room is None:
            code = room_code()
            if code not in self.rooms:
                room = Room(code, user_id, mode, duration, difficulty)
        self.rooms[room.code] = room
        await self.join(room, sid, user_id, username)
        return room

    async def join(self, room: Room, sid: str, user_id: int, username: str):
        if room.state not in ("lobby", "starting", "playing"):
            raise ValueError("Room already ended")
        if user_id in room.by_user_id:
            raise ValueError("Player already in room")
        player = Player(sid, user_id, username)
        room.players[sid] = player
        self.sid_to_room[sid] = room
        await self.sio.enter_room(sid, room.code)
        await self.sio.emit("room:joined", room.info(), to=sid)
        await self.sio.emit("room:playerJoined", player.public(), room=room.code, skip_sid=sid)

    async def leave(self, sid: str):
        room = self.sid_to_room.pop(sid, None)
        if room is None:
            return
        player = room.players.pop(sid, None)
        await self.sio.leave_room(sid, room.code)
        if player is None:
            return

        if room.state in ("starting", "playing") and len(room.players) > 0:
            await self._forfeit(room, player)
            return

        if len(room.players) == 0:
            self.rooms.pop(room.code, None)
            return

        await self.sio.emit("room:playerLeft", player.public(), room=room.code, skip_sid=sid)

    async def request_start(self, sid: str):
        room = self.room_by_sid(sid)
        if room is None:
            raise ValueError("Not in a room")
        if room.host_id != room.players[sid].user_id:
            raise ValueError("Only the host can start")
        if len(room.players) != 2:
            raise ValueError("Need two players to start")
        if room.state != "lobby":
            raise ValueError("Match already started")

        room.state = "starting"
        await self.sio.emit("match:starting", {"countdown": COUNTDOWN_SECONDS}, room=room.code)

        async def _begin():
            await asyncio.sleep(COUNTDOWN_SECONDS)
            if room.state != "starting" or len(room.players) != 2:
                room.state = "lobby" if room.state == "starting" else room.state
                return
            room.state = "playing"
            room.started_at = utcnow()
            room.ends_at = room.started_at + timedelta(seconds=room.duration)
            await self.sio.emit(
                "match:start",
                {"endsAt": room.ends_at.isoformat(), "duration": room.duration},
                room=room.code,
            )
            room._tasks.append(asyncio.create_task(self._ticker(room)))
            for player in list(room.players.values()):
                room._tasks.append(asyncio.create_task(self._player_loop(room, player)))

        room._tasks.append(asyncio.create_task(_begin()))

    async def _ticker(self, room: Room):
        try:
            while room.state == "playing" and room.ends_at and utcnow() < room.ends_at:
                remaining = int((room.ends_at - utcnow()).total_seconds())
                await self.sio.emit("timer:tick", {"remaining": remaining}, room=room.code)
                await asyncio.sleep(1)
            if room.state == "playing":
                await self._finalize(room)
        except asyncio.CancelledError:
            pass

    async def _player_loop(self, room: Room, player: Player):
        try:
            while room.state == "playing":
                question = generate_question(room.difficulty, room.used, room._qid)
                if question is None:
                    break
                player.question = question
                player.pending = None
                player.answered.clear()
                await self.sio.emit("question:new", question.client_payload(), to=player.sid)
                try:
                    await asyncio.wait_for(player.answered.wait(), timeout=ANSWER_TIMEOUT)
                except asyncio.TimeoutError:
                    continue
                answered = player.pending
                player.pending = None
                if answered is not None:
                    if answered == player.question.answer:
                        player.score += POINTS_PER_CORRECT
                        player.correct += 1
                    player.total += 1
                    await self.sio.emit(
                        "answer:result",
                        {
                            "correct": answered == player.question.answer,
                            "correctAnswer": player.question.answer,
                        },
                        to=player.sid,
                    )
                    await self.sio.emit(
                        "player:score",
                        {"playerId": player.user_id, "score": player.score},
                        room=room.code,
                    )
        except asyncio.CancelledError:
            pass

    async def submit_answer(self, sid: str, question_id: str, answer: int):
        room = self.room_by_sid(sid)
        if room is None or room.state != "playing":
            return
        player = room.players.get(sid)
        if player is None or player.question is None or player.pending is not None:
            return  # duplicate or stray answer
        if player.question.id != question_id:
            return
        player.pending = int(answer)
        player.answered.set()

    async def _forfeit(self, room: Room, leaver: Player):
        room.state = "ended"
        room._cancel_tasks()
        remaining = list(room.players.values())
        if remaining:
            winner = remaining[0]
            room.ended_at = utcnow()
            ended = room.ended_at
            await self.sio.emit(
                "match:end",
                {
                    "winner": winner.user_id,
                    "scoreboard": [p.public() for p in room.players.values()],
                    "expiry": ended.isoformat(),
                },
                room=room.code,
            )
            await asyncio.to_thread(
                save_match,
                room.code,
                room.mode,
                room.duration,
                winner.user_id,
                room.started_at,
                ended,
                [{"user_id": p.user_id, "correct": p.correct, "total": p.total} for p in room.players.values()],
            )
        await self._schedule_cleanup(room)

    async def _finalize(self, room: Room):
        room.state = "ended"
        room._cancel_tasks()
        room.ended_at = utcnow()
        ended = room.ended_at
        players_sorted = sorted(room.players.values(), key=lambda p: p.score, reverse=True)
        if len(players_sorted) >= 2 and players_sorted[0].score != players_sorted[1].score:
            winner_id = players_sorted[0].user_id
        else:
            winner_id = None
        await self.sio.emit(
            "match:end",
            {
                "winner": winner_id,
                "scoreboard": [p.public() for p in players_sorted],
                "expiry": ended.isoformat(),
            },
            room=room.code,
        )
        await asyncio.to_thread(
            save_match,
            room.code,
            room.mode,
            room.duration,
            winner_id,
            room.started_at,
            ended,
            [{"user_id": p.user_id, "correct": p.correct, "total": p.total} for p in room.players.values()],
        )
        await self._schedule_cleanup(room)

    async def _schedule_cleanup(self, room: Room):
        async def _remove():
            await asyncio.sleep(ROOM_TTL_SECONDS)
            for sid in list(room.players.keys()):
                self.sid_to_room.pop(sid, None)
            self.rooms.pop(room.code, None)

        asyncio.create_task(_remove())


manager = RoomManager()