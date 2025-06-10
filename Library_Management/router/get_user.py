from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from Library_Management.database import get_db
from Library_Management.utils import user_required

user_p = APIRouter()


@user_p.get("/user")
async def get_user(db: AsyncSession = Depends(get_db), user=Depends(user_required)):
    cursor_name = "user_cursor"

    async with db.begin():
        await db.execute(
            text(f"CALL get_user_by_id_proc(:id, :cursor)"),
            {"id": user.id, "cursor": cursor_name},
        )

        result = await db.execute(text(f"FETCH ALL FROM {cursor_name}"))
        rows = result.mappings().all()
        await db.execute(text(f"CLOSE {cursor_name}"))

    if not rows:
        raise HTTPException(status_code=404, detail="User not found")

    return rows[0]


# @user_p.get("/get_issue_book")
async def get_issue_book(
    db: AsyncSession = Depends(get_db), user=Depends(user_required)
):
    cursor_name = "user_cursor"

    async with db.begin():
        await db.execute(
            text(f"CALL get_current_issue_book(:id, :cursor)"),
            {"id": user.id, "cursor": cursor_name},
        )

        result = await db.execute(text(f"FETCH ALL FROM {cursor_name}"))
        rows = result.mappings().all()
        await db.execute(text(f"CLOSE {cursor_name}"))

    if not rows:
        raise HTTPException(status_code=404, detail="No Book Issued")

    return rows


@user_p.get("/get/books/issued", tags=["Issued Books Management"])
async def get_issue_book(
    db: AsyncSession = Depends(get_db), user=Depends(user_required)
):
    cursor_name1 = "user_cursor_1"
    cursor_name2 = "user_cursor_2"

    async with db.begin():
        await db.execute(
            text("CALL get_issue_book(:id, :cursor1, :cursor2)"),
            {"id": user.id, "cursor1": cursor_name1, "cursor2": cursor_name2},
        )

        result1 = await db.execute(text(f"FETCH ALL FROM {cursor_name1}"))
        result2 = await db.execute(text(f"FETCH ALL FROM {cursor_name2}"))

        rows1 = result1.mappings().all()
        rows2 = result2.mappings().all()

        await db.execute(text(f"CLOSE {cursor_name1}"))
        await db.execute(text(f"CLOSE {cursor_name2}"))

    if not rows1:
        raise HTTPException(status_code=404, detail="No Book Issued")

    return {"issued": rows1, "fine": rows2}
