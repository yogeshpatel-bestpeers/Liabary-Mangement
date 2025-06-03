from fastapi import FastAPI


from Library_Management.database import engine
from Library_Management.middleware.authentication import AuthenticateMiddleware

from .router import Author, Book, Category, Issued_Book, Student, authApi,get_user
from contextlib import asynccontextmanager
from fastapi import FastAPI


from .database import engine, Base
from fastapi.middleware.cors import CORSMiddleware


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


# alembic revision --autogenerate -m “Description of changes”
# alembic upgrade head
