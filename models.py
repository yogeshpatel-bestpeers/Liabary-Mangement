from pydantic import BaseModel

class Author_Created(BaseModel):
  name : str

class Book_Created(BaseModel):
  name : str
  quentity : int

class Student_Create(BaseModel):
  name : str

class Category_Created(BaseModel):
  name : str

