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

    def is_in_base(self, author_name, author_lastname):
        authors = self.query.filter_by(name=author_name).all()
        if authors is not None:
            author_id = [author.id for author in authors if author.lastname == author_lastname]
            return author_id

    def __str__(self):
        return f"Author <{self.name} {self.lastname}, id: {self.id}>"


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), index=True, unique=True)
    genre_id = db.Column(db.Integer, db.ForeignKey('genre.id'))
    publisher_id = db.Column(db.Integer, db.ForeignKey('publisher.id'))
    rating = db.Column(db.Integer)
    description = db.Column(db.Text)
    borrowed_book_card_id = db.Column(db.Integer, db.ForeignKey('borrowed_book_card.id'))

    def __str__(self):
        return f"Book <title: {self.title}, id: {self.id}>"

    def is_title_in_base(self, title):
        t = self.query.filter_by(title=title).first()
        if t is not None:
            return t.id

    def get_all(self):
        books = []

        for book in self.query.all():
            author = book.authors
            authors = [f"{names.name} {names.lastname}" for names in author]
            authors = ', '.join(authors)
            genre = Genre.query.get(book.genre_id)
            publisher = Publisher.query.get(book.publisher_id)
            status = 'na półce'
            if book.borrowed_book_card_id is not None:
                card = BorrowedBookCard.query.get(book.borrowed_book_card_id)
                if card.borrowed is True:
                    status = 'pożyczona'
            books.append({
                'id': book.id,
                'title': book.title,
                'author': authors.title(),
                'genre': genre.genre.capitalize(),
                'publisher': publisher.name.title(),
                'rating': book.rating,
                'description': book.description,
                'status': status
            })
        return books


class Borrower(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), index=True)
    lastname = db.Column(db.String(30), index=True)
    borrow = db.relationship("BorrowedBookCard", backref="borrow", lazy="dynamic")

    def __str__(self):
        return f"Borrower <{self.name} {self.lastname}>"


class BorrowedBookCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer)
    borrower_id = db.Column(db.Integer, db.ForeignKey('borrower.id'))
    date_of_loan = db.Column(db.Date)
    date_of_borrow = db.Column(db.Date, default=date.today())
    date_of_return = db.Column(db.Date)
    borrowed = db.Column(db.Boolean)
    lend = db.relationship("Book", backref="lend", lazy="dynamic")

    def __str__(self):
        return f"Borrow <{self.borrowed}>"


class Publisher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), index=True, unique=True)
    publish = db.relationship("Book", backref="publish", lazy="dynamic")

    def is_in_base(self, publisher_name):
        publisher = self.query.filter_by(name=publisher_name).first()
        if publisher is not None:
            return publisher.id

    def __str__(self):
        return f"Publisher <{self.name}, id: {self.id}>"


class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    genre = db.Column(db.String(50), index=True, unique=True)
    books = db.relationship("Book", backref="books", lazy="dynamic")

    def is_in_base(self, genre_name):
        genre = self.query.filter_by(genre=genre_name).first()
        if genre is not None:
            return genre.id

    def __str__(self):
        return f"Genre <{self.genre}, id: {self.id}>"


# def create_book(details):
#     if is_author_in_base(name=details['author_name'], lastname=details['author_lastname']) is True:
#         author = Author.guery.get(is_author_in_base(name=details['author_name'], lastname=details['author_lastname']))
#     else:
#         author = Author(name=details['author_name'], lastname=details['author_lastname'])
#     if is_genre_in_base(details['genre']) is True:
#         genre = Genre.query.get(is_genre_in_base(details['genre']))
#     else:
#         genre = Genre(genre=details['genre'])
#     if is_publisher_in_base(details['publisher_name']) is True:
#         publisher = Publisher.query.get(is_publisher_in_base(details['publisher_name']))
#     else:
#         publisher = Publisher(name=details['publisher_name'])
#
#     book = Book(title=details['title'], description=details['description'], rating=details['rating'])
#     db.session.add(book)
#     db.session.add()
#     db.session.add(book)
#     db.session.add(book)


