from sqlalchemy.orm import Session

from db import Match, MatchPlayer, engine


def save_match(
    code: str,
    mode: str,
    duration: int,
    winner_id: int | None,
    started_at,
    ended_at,
    players: list[dict],
) -> None:
    with Session(engine) as session:
        match = Match(
            code=code,
            mode=mode,
            duration=duration,
            winner_id=winner_id,
            started_at=started_at,
            ended_at=ended_at,
        )
        session.add(match)
        session.flush()
        for p in players:
            session.add(
                MatchPlayer(
                    match_id=match.id,
                    user_id=p["user_id"],
                    correct_answers=p["correct"],
                    total_answers=p["total"],
                    is_winner=p["user_id"] == winner_id,
                )
            )
        session.commit()