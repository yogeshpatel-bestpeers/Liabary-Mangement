from fastapi import FastAPI

from Library_Management import database
from Library_Management.database import engine
from Library_Management.middleware.authentication import AuthenticateMiddleware

from .router import Author, Book, Category, Issued_Book, Student, authApi

database.Base.metadata.create_all(engine)

app = FastAPI()

app.add_middleware(AuthenticateMiddleware)
app.include_router(Author.author)
app.include_router(Book.book)
app.include_router(Category.category)
app.include_router(Student.user_router)
app.include_router(Issued_Book.issuedBook)
app.include_router(authApi.auth_router)

# alembic revision --autogenerate -m “Description of changes”
# alembic upgrade head
