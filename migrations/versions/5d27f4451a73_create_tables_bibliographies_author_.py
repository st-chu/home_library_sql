"""create tables: bibliographies, author, book, borrower, borrowed book card, publisher, genre

Revision ID: 5d27f4451a73
Revises: 
Create Date: 2021-01-13 15:50:26.873116

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5d27f4451a73'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('author',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=20), nullable=True),
    sa.Column('lastname', sa.String(length=30), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_author_lastname'), 'author', ['lastname'], unique=False)
    op.create_index(op.f('ix_author_name'), 'author', ['name'], unique=False)
    op.create_table('borrower',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=20), nullable=True),
    sa.Column('lastname', sa.String(length=30), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_borrower_lastname'), 'borrower', ['lastname'], unique=False)
    op.create_index(op.f('ix_borrower_name'), 'borrower', ['name'], unique=False)
    op.create_table('genre',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('genre', sa.String(length=20), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_genre_genre'), 'genre', ['genre'], unique=False)
    op.create_table('publisher',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=20), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_publisher_name'), 'publisher', ['name'], unique=False)
    op.create_table('borrowed_book_card',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('book_id', sa.Integer(), nullable=True),
    sa.Column('borrower_id', sa.Integer(), nullable=True),
    sa.Column('date_of_loan', sa.Date(), nullable=True),
    sa.Column('date_of_return', sa.Date(), nullable=True),
    sa.Column('borrowed', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['borrower_id'], ['borrower.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('book',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=100), nullable=True),
    sa.Column('genre_id', sa.Integer(), nullable=True),
    sa.Column('publisher_id', sa.Integer(), nullable=True),
    sa.Column('rating', sa.Integer(), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('borrowed_book_card_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['borrowed_book_card_id'], ['borrowed_book_card.id'], ),
    sa.ForeignKeyConstraint(['genre_id'], ['genre.id'], ),
    sa.ForeignKeyConstraint(['publisher_id'], ['publisher.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_book_title'), 'book', ['title'], unique=False)
    op.create_table('bibliographies',
    sa.Column('book_id', sa.Integer(), nullable=False),
    sa.Column('author_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['author_id'], ['author.id'], ),
    sa.ForeignKeyConstraint(['book_id'], ['book.id'], ),
    sa.PrimaryKeyConstraint('book_id', 'author_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('bibliographies')
    op.drop_index(op.f('ix_book_title'), table_name='book')
    op.drop_table('book')
    op.drop_table('borrowed_book_card')
    op.drop_index(op.f('ix_publisher_name'), table_name='publisher')
    op.drop_table('publisher')
    op.drop_index(op.f('ix_genre_genre'), table_name='genre')
    op.drop_table('genre')
    op.drop_index(op.f('ix_borrower_name'), table_name='borrower')
    op.drop_index(op.f('ix_borrower_lastname'), table_name='borrower')
    op.drop_table('borrower')
    op.drop_index(op.f('ix_author_name'), table_name='author')
    op.drop_index(op.f('ix_author_lastname'), table_name='author')
    op.drop_table('author')
    # ### end Alembic commands ###
