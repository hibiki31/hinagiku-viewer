"""Add is_favorite

Revision ID: 43b53bf68b39
Revises: e45a2ff1d4d7
Create Date: 2024-01-05 07:38:10.155658

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '43b53bf68b39'
down_revision = 'e45a2ff1d4d7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('authors', sa.Column('is_favorite', sa.Boolean(), server_default='f', nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('authors', 'is_favorite')
    # ### end Alembic commands ###
