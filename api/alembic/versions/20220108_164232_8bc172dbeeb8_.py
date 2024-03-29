"""不要なカラムの削除

Revision ID: 8bc172dbeeb8
Revises: 428705209e04
Create Date: 2022-01-08 16:42:32.432162

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8bc172dbeeb8'
down_revision = '428705209e04'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('book_metadatas', 'ratea')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('book_metadatas', sa.Column('ratea', sa.INTEGER(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
