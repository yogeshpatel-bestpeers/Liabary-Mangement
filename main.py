from fastapi import FastAPI

from Library_Management import database
from Library_Management.database import engine

from .router import Author, Book, Category, Issued_Book, Student

database.Base.metadata.create_all(engine)

app = FastAPI()

app.include_router(Author.author)
app.include_router(Book.book)
app.include_router(Category.category)
app.include_router(Student.user_router)
app.include_router(Issued_Book.issuedBook)

# alembic revision --autogenerate -m “Description of changes”
# alembic upgrade head
