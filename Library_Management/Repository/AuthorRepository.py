from Library_Management.Repository.base import BaseRepository
from Library_Management.models import Author
from Library_Management.Schema.schema import Author_Created

class AuthorRepository(BaseRepository[Author, Author_Created]):
    def __init__(self):
        super().__init__(Author)
