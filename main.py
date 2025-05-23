from fastapi import FastAPI

from Library_Management import database
from Library_Management.database import engine
from .router import Author

database.Base.metadata.create_all(engine)

app = FastAPI()
app.include_router(Author.author)
