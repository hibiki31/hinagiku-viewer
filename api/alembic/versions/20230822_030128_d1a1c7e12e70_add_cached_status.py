"""Add cached status

Revision ID: d1a1c7e12e70
Revises: 8bc172dbeeb8
Create Date: 2023-08-22 03:01:28.044628

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd1a1c7e12e70'
down_revision = '8bc172dbeeb8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('books', sa.Column('chached', sa.Boolean(), server_default='f', nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('books', 'chached')
    # ### end Alembic commands ###
