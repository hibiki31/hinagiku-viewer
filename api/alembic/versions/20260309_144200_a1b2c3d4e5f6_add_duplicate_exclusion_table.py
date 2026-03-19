"""add_duplicate_exclusion_table

Revision ID: a1b2c3d4e5f6
Revises: b3c4d5e6f7a8
Create Date: 2026-03-09 14:42:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = 'b3c4d5e6f7a8'
branch_labels = None
depends_on = None


def upgrade():
    # 重複除外ペアテーブルを作成
    # book_uuid_1 < book_uuid_2 になるよう正規化して格納する
    op.create_table(
        'duplicate_exclusion',
        sa.Column('book_uuid_1', sa.String(), nullable=False),
        sa.Column('book_uuid_2', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['book_uuid_1'], ['books.uuid'], onupdate='CASCADE', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['book_uuid_2'], ['books.uuid'], onupdate='CASCADE', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('book_uuid_1', 'book_uuid_2'),
        sa.UniqueConstraint('book_uuid_1', 'book_uuid_2', name='uq_duplicate_exclusion'),
    )
    # インデックス追加（検索高速化）
    op.create_index('idx_duplicate_exclusion_uuid1', 'duplicate_exclusion', ['book_uuid_1'])
    op.create_index('idx_duplicate_exclusion_uuid2', 'duplicate_exclusion', ['book_uuid_2'])


def downgrade():
    # インデックス削除
    op.drop_index('idx_duplicate_exclusion_uuid2', 'duplicate_exclusion')
    op.drop_index('idx_duplicate_exclusion_uuid1', 'duplicate_exclusion')
    # テーブル削除
    op.drop_table('duplicate_exclusion')
