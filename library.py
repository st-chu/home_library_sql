# library.py

from app import app, db
from app.models import Book, Author, Genre, Publisher, Borrower, BorrowedBookCard

@app.shell_context_processor
def make_shell_context():
    return {
        "db": db,
        "Book": Book,
        "Author": Author,
        "Genre": Genre,
        "Publisher": Publisher,
        "Borrower": Borrower,
        "BorrowedBookCard": BorrowedBookCard
    }
