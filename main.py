from fastapi import FastAPI
from Library_Management import models

from Library_Management.database import engine

models.Base.metadata.create_all(engine)

app =FastAPI()
