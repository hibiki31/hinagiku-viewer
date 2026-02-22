"""add_publication_date_and_model_number

Revision ID: b3c4d5e6f7a8
Revises: 59a15d1f226d
Create Date: 2026-02-22 18:32:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'b3c4d5e6f7a8'
down_revision = '59a15d1f226d'
branch_labels = None
depends_on = None


def upgrade():
    # booksテーブルに出版日カラムを追加
    op.add_column('books', sa.Column('publication_date', sa.Date(), nullable=True, comment='出版日'))
    # booksテーブルに型番カラムを追加
    op.add_column('books', sa.Column('model_number', sa.String(), nullable=True, comment='型番'))


def downgrade():
    op.drop_column('books', 'model_number')
    op.drop_column('books', 'publication_date')
