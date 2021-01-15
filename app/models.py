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

    def add_author(self, author_name, author_lastname):
        _id = self.is_in_base(author_name=author_name, author_lastname=author_lastname)
        if not bool(_id):
            author = Author(name=author_name, lastname=author_lastname)
            db.session.add(author)
            db.session.commit()
            return author
        return self.query.get(_id[0])

    def update(self, author_id, author_name, author_lastname):
        author = self.query.get(author_id)
        authors = self.query.filter_by(lastname=author_lastname).all()
        if authors is not None:
            for names in authors:
                if names.name == author_name and names.lastname == author_lastname:
                    return names
        author.name = author_name
        author.lastname = author_lastname
        db.session.commit()
        return author

    def delete(self, author_id):
        author = self.query.get(author_id)
        db.session.delete(author)
        db.session.commit()

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

    def get_authors(self, book_id):
        book = self.query.get(book_id)
        author = book.authors
        authors = [{'name': names.name.title(), 'lastname': names.lastname.title()} for names in author]
        return authors

    def get_one(self, book_id: int):
        book = self.query.get(book_id)
        author = book.get_authors(book.id)
        genre = Genre.query.get(book.genre_id)
        publisher = Publisher.query.get(book.publisher_id)
        status = BorrowedBookCard().get_status(book.id)
        book = {
            'id': book.id,
            'title': book.title,
            'author_name': author[0]['name'],
            'author_lastname': author[0]['lastname'],
            'genre': genre.genre,
            'publisher': publisher.name,
            'rating': book.rating,
            'description': book.description,
            'status': status
        }
        return book

    def get_all(self):
        books = []

        for book in self.query.all():
            authors = self.get_authors(book.id)
            author = [f"{name['name']} {name['lastname']}" for name in authors]
            authors = ', '.join(author)
            genre = Genre.query.get(book.genre_id).genre
            publisher = Publisher.query.get(book.publisher_id).name
            status = BorrowedBookCard().get_status(book.id)
            books.append({
                'id': book.id,
                'title': book.title,
                'author': authors,
                'genre': genre,
                'publisher': publisher,
                'rating': book.rating,
                'description': book.description,
                'status': status
            })
        return books

    def add_title(self, title, rating, description):
        id = self.is_title_in_base(title=title)
        if id is None:
            book = Book(
                title=title.title(),
                rating=rating,
                description=description
            )
            db.session.add(book)
            db.session.commit()
            return book
        else:
            return self.query.get(id)

    def add_book(self, details):

        book = self.add_title(
            title=details['title'].title(),
            rating=details['rating'],
            description=details['description']
        )
        author = Author().add_author(
            author_name=details['author_name'].title(),
            author_lastname=details['author_lastname'].title()
        )
        book.authors.append(author)
        genre = Genre().add_genre(genre=details['genre'].capitalize())
        genre.books.append(book)
        publisher = Publisher().add_publisher(publisher=details['publisher'].title())
        publisher.books.append(book)
        db.session.commit()

    def update(self, book_id, details):
        book = self.query.get(book_id)
        genre = Genre().update(book.genre_id, details['genre'].capitalize())
        publisher = Publisher().update(book.publisher_id, details['publisher'].title())
        author = Author().update(
            book.authors[0].id,
            details['author_name'].title(),
            details['author_lastname'].title())
        book.authors.clear()
        book.authors.append(author)
        book.publisher_id = publisher.id
        book.genre_id = genre.id
        book.title = details['title'].title()
        book.rating = details['rating']
        book.description = details['description']
        db.session.commit()

    def delete(self, book_id):
        book = self.query.get(book_id)
        db.session.delete(book)
        db.session.commit()


class Borrower(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), index=True)
    lastname = db.Column(db.String(30), index=True)
    borrow = db.relationship("BorrowedBookCard", backref="borrow", lazy='subquery')

    def is_in_base(self, borrower_name, borrower_lastname):
        borrower = self.query.filter_by(lastname=borrower_lastname).all()
        if borrower is not None:
            borrower_id = [name.id for name in borrower if name.name == borrower_name]
            return borrower_id

    def add_borrower(self, borrower_name, borrower_lastname):
        _id = self.is_in_base(borrower_name=borrower_name.title(), borrower_lastname=borrower_lastname.title())
        if not bool(_id):
            borrower = Author(name=borrower_name.title(), lastname=borrower_lastname.title())
            db.session.add(borrower)
            db.session.commit()
            return borrower
        return self.query.get(_id[0])

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
    lend = db.relationship("Book", backref="lend", lazy='subquery')

    def get_status(self, book_id):
        book = self.query.get(book_id)
        if book is not None:
            card = self.query.get(book.borrowed_book_card_id)
            if card.borrowed is True:
                return 'pożyczona'
        return 'na półce'

    def __str__(self):
        return f"Borrow <{self.borrowed}>"


class Publisher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), index=True, unique=True)
    books = db.relationship("Book", backref="publish", lazy='subquery')

    def is_in_base(self, publisher_name):
        publisher = self.query.filter_by(name=publisher_name).first()
        if publisher is not None:
            return publisher.id

    def add_publisher(self, publisher: str):
        id = self.is_in_base(publisher_name=publisher)
        if id is None:
            publisher = Publisher(name=publisher)
            db.session.add(publisher)
            db.session.commit()
            return publisher
        else:
            return self.query.get(id)

    def delete(self, publisher_id):
        publisher = self.query.get(publisher_id)
        db.session.delete(publisher)
        db.session.commit()

    def update(self, publisher_id, name):
        publisher = self.query.get(publisher_id)
        if self.query.filter_by(name=name) is not None:
            return self.query.filter_by(name=name).first()
        publisher.name = name
        db.session.commit()
        return publisher

    def __str__(self):
        return f"Publisher <{self.name}, id: {self.id}>"


class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    genre = db.Column(db.String(50), index=True, unique=True)
    books = db.relationship("Book", backref="genre", lazy='subquery')

    def is_in_base(self, genre_name):
        genre = self.query.filter_by(genre=genre_name).first()
        if genre is not None:
            return genre.id

    def add_genre(self, genre: str):
        id = self.is_in_base(genre_name=genre)
        if id is None:
            genre = Genre(genre=genre)
            db.session.add(genre)
            db.session.commit()
            return genre
        else:
            return self.query.get(id)

    def delete(self, genre_id):
        genre = self.query.get(genre_id)
        db.session.delete(genre)
        db.session.commit()

    def update(self, genre_id, name):
        genre = self.query.get(genre_id)
        if self.query.filter_by(genre=name) is not None:
            return self.query.filter_by(genre=name).first()
        genre.genre = name
        db.session.commit()
        return genre

    def __str__(self):
        return f"Genre <{self.genre}, id: {self.id}>"
