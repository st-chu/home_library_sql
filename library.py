# library.py

from flask import Flask, request, render_template, redirect, url_for
from app import app, db
from app.models import Book, Author, Genre, Publisher, Borrower, BorrowedBookCard
from app.forms import BookForm, Borrow


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


@app.route("/library/", methods=['GET'])
def library():
    form = BookForm()
    books = Book().get_all()
    return render_template('library.html', form=form, books=books)


@app.route("/library/", methods=['POST'])
def add_new_book():
    form = BookForm()
    error = ''
    if form.validate_on_submit():
        details = form.data
        if bool(Book().is_title_in_base(details['title'])) is True:
            error = "książka już istnieje w bazie danych"
            return render_template('library.html', form=form, books=Book().get_all(), error=error)
        Book().add_book(details)
        return redirect(url_for('library'))


@app.route("/library/<int:book_id>/", methods=['GET'])
def book_details(book_id):
    book = Book().get_one(book_id)
    form = BookForm(data=book)
    return render_template('book.html', form=form, book_id=book_id, book=book)


@app.route("/library/<int:book_id>/", methods=['POST'])
def book_update(book_id):
    book = Book().get_one(book_id)
    form = BookForm(data=book)
    error = ''
    if form.validate_on_submit():
        Book().update(book_id, form.data)
        return redirect(url_for("library"))
    return render_template('book.html', form=form, book_id=book_id)


@app.route("/delete/<int:book_id>/", methods=['POST'])
def delete_book(book_id):
    Book().delete(book_id)
    return redirect(url_for('library'))


@app.route("/library/lend/<int:book_id>/", methods=['GET'])
def lend(book_id):
    form = Borrow()
    return render_template('lend.html', form=form, book_id=book_id)


@app.route("/borrow/<int:book_id>/", methods=['POST'])
def borrow(book_id):
    form = Borrow()
    data = form.data
    if form.validate_on_submit():
        BorrowedBookCard().borrow_book(book_id, data['borrower_name'], data['borrower_lastname'])
        return redirect(url_for('book_details', book_id=book_id))
    return redirect(url_for('book_details', book_id=book_id))


@app.route("/giveback/<int:book_id>/", methods=['GET'])
def give_back(book_id):
    BorrowedBookCard().give_back_book(book_id)
    return redirect(url_for('book_details', book_id=book_id))