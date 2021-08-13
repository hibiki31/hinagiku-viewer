"""empty message

Revision ID: c21aa9cb2941
Revises: 
Create Date: 2021-08-13 09:00:19.007877

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c21aa9cb2941'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('author',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('genre',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('publisher',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('series',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('tag',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('user',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('password', sa.String(), nullable=True),
    sa.Column('is_admin', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('library',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('user_id', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('book',
    sa.Column('uuid', sa.String(), nullable=False),
    sa.Column('user_id', sa.String(), nullable=False),
    sa.Column('size', sa.Numeric(), nullable=False),
    sa.Column('sha1', sa.String(), nullable=False),
    sa.Column('page', sa.Integer(), nullable=False),
    sa.Column('add_date', sa.DateTime(), nullable=False),
    sa.Column('file_date', sa.DateTime(), nullable=False),
    sa.Column('import_file_name', sa.String(), nullable=False),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('series_no', sa.Integer(), nullable=True),
    sa.Column('library_id', sa.Integer(), nullable=False),
    sa.Column('genre_id', sa.Integer(), nullable=True),
    sa.Column('publisher_id', sa.Integer(), nullable=True),
    sa.Column('series_id', sa.Integer(), nullable=True),
    sa.Column('is_shered', sa.Boolean(), nullable=True),
    sa.Column('state', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['genre_id'], ['genre.id'], ),
    sa.ForeignKeyConstraint(['library_id'], ['library.id'], ),
    sa.ForeignKeyConstraint(['publisher_id'], ['publisher.id'], ),
    sa.ForeignKeyConstraint(['series_id'], ['series.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('uuid')
    )
    op.create_index(op.f('ix_book_uuid'), 'book', ['uuid'], unique=False)
    op.create_table('library_to_user',
    sa.Column('library_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['library_id'], ['library.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], )
    )
    op.create_table('book_to_author',
    sa.Column('book_uuid', sa.String(), nullable=True),
    sa.Column('author_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['author_id'], ['author.id'], ),
    sa.ForeignKeyConstraint(['book_uuid'], ['book.uuid'], )
    )
    op.create_table('books_metadata',
    sa.Column('user_id', sa.String(), nullable=False),
    sa.Column('book_uuid', sa.String(), nullable=False),
    sa.Column('last_open_date', sa.DateTime(), nullable=True),
    sa.Column('read_times', sa.Integer(), nullable=True),
    sa.Column('open_page', sa.Integer(), nullable=True),
    sa.Column('rate', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['book_uuid'], ['book.uuid'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_id', 'book_uuid')
    )
    op.create_table('tag_to_book',
    sa.Column('book_uuid', sa.String(), nullable=True),
    sa.Column('tags_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['book_uuid'], ['book.uuid'], ),
    sa.ForeignKeyConstraint(['tags_id'], ['tag.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tag_to_book')
    op.drop_table('books_metadata')
    op.drop_table('book_to_author')
    op.drop_table('library_to_user')
    op.drop_index(op.f('ix_book_uuid'), table_name='book')
    op.drop_table('book')
    op.drop_table('library')
    op.drop_table('user')
    op.drop_table('tag')
    op.drop_table('series')
    op.drop_table('publisher')
    op.drop_table('genre')
    op.drop_table('author')
    # ### end Alembic commands ###