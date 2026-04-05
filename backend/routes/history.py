"""User history routes backed by MongoDB."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from core.security import get_current_user
from db.mongo import get_db

router = APIRouter(prefix="/history")


@router.get("")
async def get_history(current_user: dict = Depends(get_current_user)) -> list[dict]:
    db = get_db()
    rows = list(
        db.analyses.find({"user_id": current_user["id"]})
        .sort("created_at", -1)
        .limit(50)
    )

    history: list[dict] = []
    for row in rows:
        history.append(
            {
                "id": str(row["_id"]),
                "created_at": row["created_at"],
                "project_input": row["project_input"],
                "result": row["result"],
            }
        )
    return history
