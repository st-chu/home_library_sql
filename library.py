# library.py

from flask import Flask, request, render_template, redirect, url_for
from app import app, db
from app.models import Book, Author, Genre, Publisher, Borrower, BorrowedBookCard
# from app.forms import Book, Borrow


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


# @app.route("/library/", methods=['GET'])
# def library():
#     form = Book()
#     books = get_all()
#     return render_template('library.html', form=form, books=books)
#
#
# @app.route("/library/", methods=['POST'])
# def add_new_book():
#     form = Book()
#     error = ''
#     if form.validate_on_submit():
#         details = form.data
#         if is_title_in_base() is True:
#             error = "książka już istnieje w bazie danych"
#             return render_template('library.html', form=form, books=get_all(), error=error)

