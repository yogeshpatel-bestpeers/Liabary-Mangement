from fastapi import status
from starlette.middleware.base import BaseHTTPMiddleware

from Library_Management.database import get_db
from Library_Management.utils import Helper

auth = Helper()

from fastapi import HTTPException
from fastapi.responses import JSONResponse


class AuthenticateMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request, call_next):
        public_routes = ["/login", "/signup", "/docs", "/openapi.json", "/favicon.ico"]

        if request.url.path in public_routes:
            return await call_next(request)

        try:
            token = request.headers.get("Authorization")
            if not token:
                raise HTTPException(
                    detail="Not authenticated", status_code=status.HTTP_401_UNAUTHORIZED
                )

            if not token.startswith("Bearer "):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token format",
                )

            token = token.split(" ")[1]
            async for db in get_db():
                user = await auth.get_current_user(token, db)
                request.state.user = user
                break

            return await call_next(request)

        except HTTPException as exc:
            return JSONResponse(
                status_code=exc.status_code, content={"detail": exc.detail}
            )
        except Exception as exc:
            return JSONResponse(status_code=500, content={"detail": str(exc)})
