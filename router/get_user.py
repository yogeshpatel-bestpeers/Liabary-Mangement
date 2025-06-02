from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from Library_Management.database import get_db
from Library_Management.utils import user_required

user_p = APIRouter()

@user_p.get("/user")
async def get_user(db: AsyncSession = Depends(get_db), user = Depends(user_required)):
    cursor_name = "user_cursor"

    async with db.begin():
        await db.execute(
                text(f"CALL get_user_by_id_proc(:id, :cursor)"),
                {"id":  user.id, "cursor": cursor_name}
            )

        result = await db.execute(text(f"FETCH ALL FROM {cursor_name}"))
        rows = result.mappings().all()
        await db.execute(text(f"CLOSE {cursor_name}"))

    if not rows:
        raise HTTPException(status_code=404, detail="User not found")

    return rows[0]
