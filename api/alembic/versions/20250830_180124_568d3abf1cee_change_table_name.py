"""Change table name

Revision ID: 568d3abf1cee
Revises: 43b53bf68b39
Create Date: 2025-08-30 18:01:24.877214

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '568d3abf1cee'
down_revision = '43b53bf68b39'
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table('librarys', 'libraries')

def downgrade():
    op.rename_table('libraries', 'librarys')
