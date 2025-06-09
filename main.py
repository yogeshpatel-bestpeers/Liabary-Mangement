from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .middleware.authentication import AuthenticateMiddleware
from .router import (Author, Book, CartItem, Category, Issued_Book, Student,
                     authApi, get_user)


def create_app(engine):
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        try:
            yield
        finally:
            await engine.dispose()

    app = FastAPI(lifespan=lifespan)
    origins = [
        "http://localhost.tiangolo.com",
        "https://localhost.tiangolo.com",
        "http://localhost",
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(AuthenticateMiddleware)

    app.include_router(Author.author)
    app.include_router(Book.book)
    app.include_router(Category.category)
    app.include_router(Student.user_router)
    app.include_router(Issued_Book.issuedBook)
    app.include_router(authApi.auth_router)
    app.include_router(get_user.user_p)
    app.include_router(CartItem.cart)

    return app


app = create_app(engine)
