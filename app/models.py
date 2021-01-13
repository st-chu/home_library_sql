# app/models.py

from app import db
from datetime import date


bibliographies = db.Table(
    'bibliographies',
    db.Column('book_id', db.Integer, db.ForeignKey('book.id'), primary_key=True),
    db.Column('author_id', db.Integer, db.ForeignKey('author.id'), primary_key=True)
)


class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), index=True)
    lastname = db.Column(db.String(30), index=True)
    bibliographies = db.relationship('Book', secondary=bibliographies, backref="authors", lazy='subquery')

    def __str__(self):
        return f"Author <{self.name} {self.lastname}, id: {self.id}>"


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), index=True)
    genre_id = db.Column(db.Integer, db.ForeignKey('genre.id'))
    publisher_id = db.Column(db.Integer, db.ForeignKey('publisher.id'))
    rating = db.Column(db.Integer)
    description = db.Column(db.Text)
    borrowed_book_card_id = db.Column(db.Integer, db.ForeignKey('borrowed_book_card.id'))

    def __str__(self):
        return f"Book <title: {self.title}, id: {self.id}>"


class Borrower(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), index=True)
    lastname = db.Column(db.String(30), index=True)
    cards = db.relationship("BorrowedBookCard", backref="cards", lazy="dynamic")

    def __str__(self):
        return f"Borrower <{self.name} {self.lastname}>"


class BorrowedBookCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer)
    borrower_id = db.Column(db.Integer, db.ForeignKey('borrower.id'))
    date_of_loan = db.Column(db.Date, default=date.today())
    date_of_return = db.Column(db.Date)
    borrowed = db.Column(db.Boolean)
    books = db.relationship("Book", backref="books", lazy="dynamic")


class Publisher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), index=True)
    books = db.relationship("Book", backref="books", lazy="dynamic")

    def __str__(self):
        return f"Publisher <{self.name}, id: {self.id}>"


class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    genre = db.Column(db.String(20), index=True)
    books = db.relationship("Book", backref="books", lazy="dynamic")

    def __str__(self):
        return f"Genre <{self.genre}, id: {self.id}>"

