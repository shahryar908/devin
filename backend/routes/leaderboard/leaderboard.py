from sqlalchemy import case, desc, func, select
from fastapi import APIRouter, HTTPException

from db import Match, MatchPlayer, User
from security import SessionDep

router = APIRouter(tags=["leaderboard", "users"])

WINS = func.sum(case((MatchPlayer.is_winner == True, 1), else_=0))  # noqa: E712


@router.get("/leaderboard")
def leaderboard(session: SessionDep, limit: int = 50) -> list[dict]:
    stmt = (
        select(
            User.username,
            User.id.label("userId"),
            func.count(MatchPlayer.match_id).label("matches"),
            WINS.label("wins"),
            func.sum(MatchPlayer.correct_answers).label("correct"),
            func.sum(MatchPlayer.total_answers).label("answers"),
        )
        .join(MatchPlayer, MatchPlayer.user_id == User.id)
        .group_by(User.id)
        .order_by(desc("wins"), desc("correct"))
        .limit(limit)
    )
    rows = session.execute(stmt).all()
    result = []
    for row in rows:
        answers = row.answers or 0
        result.append(
            {
                "userId": row.userId,
                "username": row.username,
                "matches": row.matches,
                "wins": row.wins or 0,
                "correct": row.correct or 0,
                "accuracy": round(row.correct / answers, 3) if answers else 0.0,
            }
        )
    return result


@router.get("/users/{user_id}/matches")
def user_matches(user_id: int, session: SessionDep) -> list[dict]:
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(404, "User not found")
    stmt = (
        select(Match, MatchPlayer)
        .join(MatchPlayer, MatchPlayer.match_id == Match.id)
        .where(MatchPlayer.user_id == user_id)
        .order_by(desc(Match.started_at))
    )
    rows = session.execute(stmt).all()
    return [
        {
            "id": row.Match.id,
            "code": row.Match.code,
            "mode": row.Match.mode,
            "duration": row.Match.duration,
            "winnerId": row.Match.winner_id,
            "startedAt": row.Match.started_at.isoformat(),
            "endedAt": row.Match.ended_at.isoformat(),
            "correctAnswers": row.MatchPlayer.correct_answers,
            "totalAnswers": row.MatchPlayer.total_answers,
            "isWinner": row.MatchPlayer.is_winner,
        }
        for row in rows
    ]


@router.get("/users/{user_id}/stats")
def user_stats(user_id: int, session: SessionDep) -> dict:
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(404, "User not found")
    stmt = (
        select(
            func.count(MatchPlayer.match_id).label("matches"),
            WINS.label("wins"),
            func.sum(MatchPlayer.correct_answers).label("correct"),
            func.sum(MatchPlayer.total_answers).label("answers"),
        )
        .where(MatchPlayer.user_id == user_id)
    )
    row = session.execute(stmt).one()
    answers = row.answers or 0
    return {
        "userId": user_id,
        "username": user.username,
        "totalMatches": row.matches or 0,
        "wins": row.wins or 0,
        "totalCorrect": row.correct or 0,
        "totalAnswers": answers,
        "accuracy": round(row.correct / answers, 3) if answers else 0.0,
    }