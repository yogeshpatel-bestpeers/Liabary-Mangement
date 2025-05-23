from pydantic import BaseModel


class Author_Created(BaseModel):
  name : str

class Book_Created(BaseModel):
  name : str
  quantity : int
  author_id : str
  category_id : str

class Category_Created(BaseModel):
  name : str

class User_Created(BaseModel):
  email : str
  first_name : str
  last_name : str
  password : str


