from .database import Base
from sqlalchemy.orm import Mapped,mapped_column,relationship
from sqlalchemy import ForeignKey
from typing import List
import uuid
# Author, Category, Book, Course, Student, IssuedBook, and Fine
