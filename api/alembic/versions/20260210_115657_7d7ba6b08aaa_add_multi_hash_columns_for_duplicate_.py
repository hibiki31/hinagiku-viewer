"""add_multi_hash_columns_for_duplicate_detection

Revision ID: 7d7ba6b08aaa
Revises: 568d3abf1cee
Create Date: 2026-02-10 11:56:57.081404

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7d7ba6b08aaa'
down_revision = '568d3abf1cee'
branch_labels = None
depends_on = None


def upgrade():
    # phash と dhash カラムを追加（マルチハッシュ戦略用）
    op.add_column('books', sa.Column('phash', sa.String(), nullable=True))
    op.add_column('books', sa.Column('dhash', sa.String(), nullable=True))
    
    # インデックス作成（検索性能向上）
    op.create_index('idx_books_ahash', 'books', ['ahash'])
    op.create_index('idx_books_phash', 'books', ['phash'])
    op.create_index('idx_books_dhash', 'books', ['dhash'])
    
    # 重複検出設定テーブル
    op.create_table(
        'duplicate_settings',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('ahash_threshold', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('phash_threshold', sa.Integer(), nullable=False, server_default='12'),
        sa.Column('dhash_threshold', sa.Integer(), nullable=False, server_default='15'),
        sa.Column('lsh_bands', sa.Integer(), nullable=False, server_default='16'),
        sa.Column('lsh_band_size', sa.Integer(), nullable=False, server_default='16'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now())
    )
    
    # デフォルト設定を挿入
    op.execute(
        "INSERT INTO duplicate_settings (id, ahash_threshold, phash_threshold, dhash_threshold, lsh_bands, lsh_band_size) "
        "VALUES (1, 10, 12, 15, 16, 16)"
    )
    
    # duplicationテーブルにインデックス追加
    op.create_index('idx_duplication_id', 'duplication', ['duplication_id'])
    op.create_index('idx_duplication_score', 'duplication', ['score'])


def downgrade():
    # インデックス削除
    op.drop_index('idx_duplication_score', 'duplication')
    op.drop_index('idx_duplication_id', 'duplication')
    op.drop_index('idx_books_dhash', 'books')
    op.drop_index('idx_books_phash', 'books')
    op.drop_index('idx_books_ahash', 'books')
    
    # テーブル削除
    op.drop_table('duplicate_settings')
    
    # カラム削除
    op.drop_column('books', 'dhash')
    op.drop_column('books', 'phash')
