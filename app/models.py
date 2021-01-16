# app/models.py

from app import db
from typing import List, Dict, Union
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

    def is_in_base(self, author_name: str, author_lastname: str) -> List[int]:
        """checks if the author is in the database"""
        _authors = self.query.filter_by(name=author_name).all()
        if _authors is not None:
            author_id = [author.id for author in _authors if author.lastname == author_lastname]
            return author_id

    def add_author(self, author_name: str, author_lastname: str) -> object:
        """adds author to database and returns it, if author exists in database returns existing author"""
        _id = self.is_in_base(author_name=author_name, author_lastname=author_lastname)
        if not bool(_id):
            author = Author(name=author_name, lastname=author_lastname)
            db.session.add(author)
            db.session.commit()
            return author
        return self.query.get(_id[0])

    def update(self, author_id: int, author_name: str, author_lastname: str) -> object:
        """changes author's data and returns it, if author has more than one book, creates new author and returns him"""
        author = self.query.get(author_id)
        if len(author.bibliographies) > 1 and any([
            author.name != author_name,
            author.lastname != author_lastname
        ]):
            author = Author(name=author_name, lastname=author_lastname)
            db.session.add(author)
            db.session.commit()
            return author
        author.name = author_name
        author.lastname = author_lastname
        db.session.commit()
        return author

    def delete(self, author_id: int) -> None:
        """removes the author"""
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

    def is_title_in_base(self, title: str) -> int:
        t = self.query.filter_by(title=title).first()
        if t is not None:
            return t.id

    def get_authors(self, book_id: int) -> List[Dict[str, str]]:
        """gets the authors of the book and returns a list of authors"""
        book = self.query.get(book_id)
        author = book.authors
        authors = [{'name': names.name.title(), 'lastname': names.lastname.title()} for names in author]
        return authors

    def get_one(self, book_id: int) -> object:
        """gets the details of the book"""
        book = self.query.get(book_id)
        author = book.get_authors(book.id)
        genre = Genre.query.get(book.genre_id)
        publisher = Publisher.query.get(book.publisher_id)
        status = BorrowedBookCard().get_status(book_id)
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
        print(author)
        return book

    def get_all(self):
        """downloads books from database and returns book list"""
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

    def add_title(self, title: str, rating: int, description: str) -> object:
        """adds a new title to the database and returns it,
        if the title is already in the database returns the existing title"""
        _id = self.is_title_in_base(title=title)
        if _id is None:
            book = Book(
                title=title.title(),
                rating=rating,
                description=description
            )
            db.session.add(book)
            db.session.commit()
            return book
        return self.query.get(_id)

    def add_book(self, details) -> None:
        """adds a new book to the database"""
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

    def update(self, book_id: int, details: Dict[str, Union[str, int]]) -> None:
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

    def delete(self, book_id: int) -> None:
        """removes the book from the database"""
        book = self.query.get(book_id)
        db.session.delete(book)
        db.session.commit()


class Borrower(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), index=True)
    lastname = db.Column(db.String(30), index=True)
    borrow = db.relationship("BorrowedBookCard", backref="borrow", lazy='subquery')

    def is_in_base(self, borrower_name: str, borrower_lastname: str) -> List[int]:
        """checks if the borrower is in the database and returns its id"""
        borrower = self.query.filter_by(lastname=borrower_lastname).all()
        if borrower is not None:
            borrower_id = [name.id for name in borrower if name.name == borrower_name]
            return borrower_id

    def add_borrower(self, borrower_name: str, borrower_lastname: str) -> object:
        """adds borrower to database and returns it, if borrower is in database it returns existing one"""
        _id = self.is_in_base(borrower_name=borrower_name.title(), borrower_lastname=borrower_lastname.title())
        if not bool(_id):
            borrower = Borrower(name=borrower_name.title(), lastname=borrower_lastname.title())
            db.session.add(borrower)
            db.session.commit()
            return borrower
        return self.query.get(_id)

    def __str__(self):
        return f"Borrower <{self.name} {self.lastname}>"


class BorrowedBookCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer)
    borrower_id = db.Column(db.Integer, db.ForeignKey('borrower.id'))
    date_of_loan = db.Column(db.Date)
    date_of_borrow = db.Column(db.Date)
    date_of_return = db.Column(db.Date)
    borrowed = db.Column(db.Boolean)
    lend = db.relationship("Book", backref="lend", lazy='subquery')

    def is_in_base(self, book_id: int) -> int:
        """checks if the card is in the database and returns the card id"""
        card = self.query.filter_by(book_id=book_id).first()
        if card is not None:
            return card.id

    def add_card(self, book_id: int) -> object:
        """adds a card to the database and returns it, if the card exists, it returns the existing one"""
        _id = self.is_in_base(book_id)
        if _id is None:
            card = BorrowedBookCard(borrowed=False)
            db.session.add(card)
            db.session.commit()
            return card
        return self.query.get(_id)

    def borrow_book(self, book_id: int, borrower_name: str, borrower_lastname: str) -> None:
        """sets borrowed to True"""
        book = Book().query.get(book_id)
        card = self.add_card(book_id)
        borrower = Borrower().add_borrower(borrower_name, borrower_lastname)
        borrower.borrow.append(card)
        card.book_id = book_id
        book.borrowed_book_card_id = card.id
        card.borrowed = True
        db.session.commit()

    def give_back_book(self, book_id: int) -> None:
        """sets borrowed to False"""
        card = self.add_card(book_id)
        card.borrowed = False
        card.borrower_id = None
        db.session.commit()

    def get_status(self, book_id: int) -> str:
        """checks if the book is on loan and returns its status"""
        book = Book().query.get(book_id)
        card_id = book.borrowed_book_card_id
        if card_id:
            card = self.query.get(card_id)
            if card.borrowed is True:
                return 'pożyczona'
        return 'na półce'

    def __str__(self):
        return f"Borrow <{self.borrowed}>"


class Publisher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), index=True, unique=True)
    books = db.relationship("Book", backref="publish", lazy='subquery')

    def is_in_base(self, publisher_name: str) -> int:
        """checks if the publisher is in the database and returns its id"""
        publisher = self.query.filter_by(name=publisher_name).first()
        if publisher is not None:
            return publisher.id

    def add_publisher(self, publisher: str):
        """adds the publisher to the database and returns it,
        if the publisher is in the database, it returns the existing one"""
        _id = self.is_in_base(publisher_name=publisher)
        if _id is None:
            publisher = Publisher(name=publisher)
            db.session.add(publisher)
            db.session.commit()
            return publisher
        return self.query.get(_id)

    def delete(self, publisher_id: int) -> None:
        """removes the publisher from the database"""
        publisher = self.query.get(publisher_id)
        db.session.delete(publisher)
        db.session.commit()

    def update(self, publisher_id: int, name: str) -> object:
        """changes the publisher's data and returns the publisher,
        if the publisher has more than one book, add a new publisher to the database and return it"""
        publisher = self.query.get(publisher_id)
        if len(publisher.books) > 1 and publisher.name != name:
            publisher = Publisher(name=name)
            db.session.add(publisher)
            db.session.commit()
            return publisher
        publisher.name = name
        db.session.commit()
        return publisher

    def __str__(self):
        return f"Publisher <{self.name}, id: {self.id}>"


class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    genre = db.Column(db.String(50), index=True, unique=True)
    books = db.relationship("Book", backref="genre", lazy='subquery')

    def is_in_base(self, genre_name: str) -> int:
        """checks if genre is in the database and returns the genre id"""
        genre = self.query.filter_by(genre=genre_name).first()
        if genre is not None:
            return genre.id

    def add_genre(self, genre: str) -> object:
        """adds genre to database and returns it, if genre is in database returns existing one"""
        _id = self.is_in_base(genre_name=genre)
        if _id is None:
            genre = Genre(genre=genre)
            db.session.add(genre)
            db.session.commit()
            return genre
        return self.query.get(_id)

    def delete(self, genre_id: int) -> None:
        """removes genre from the database"""
        genre = self.query.get(genre_id)
        db.session.delete(genre)
        db.session.commit()

    def update(self, genre_id: int, name: str):
        """renames genre and returns them, if there are more books in the genre, creates new ones and returns them"""
        genre = self.query.get(genre_id)
        if len(genre.books) > 1 and genre.genre != name:
            genre = Genre(genre=name)
            db.session.add(genre)
            db.session.commit()
            return genre
        genre.genre = name
        db.session.commit()
        return genre

    def __str__(self):
        return f"Genre <{self.genre}, id: {self.id}>"
