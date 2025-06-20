from Library_Management.Repository.base import BaseRepository
from Library_Management.models import Author,Book
from Library_Management.Schema.schema import Author_Created,Book_Created

class AuthorRepository(BaseRepository[Author, Author_Created]):
    def __init__(self):
        super().__init__(Author)

class BookRepository(BaseRepository[Book, Book_Created]):
    def __init__(self):
        super().__init__(Book)