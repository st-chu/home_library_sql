from flask_wtf import FlaskForm
from wtforms import TextAreaField, StringField, SelectField
from wtforms.validators import DataRequired, Length


class BookForm(FlaskForm):
    author_name = StringField('imię autor', validators=[DataRequired(), Length(max=20)])
    author_lastname = StringField('nazwisko autora', validators=[DataRequired(), Length(max=30)])
    title = StringField('tytuł', validators=[DataRequired(), Length(max=100)])
    genre = StringField('gatunek', validators=[DataRequired(), Length(max=100)])
    publisher = StringField('wydawca', validators=[Length(max=50), DataRequired()])
    description = TextAreaField('opis')
    rating = SelectField('ocena', choices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])


class Borrow(FlaskForm):
    borrower_name = StringField('imię', validators=[DataRequired(), Length(max=20)])
    borrower_lastname = StringField('nazwisko', validators=[DataRequired(), Length(max=30)])
