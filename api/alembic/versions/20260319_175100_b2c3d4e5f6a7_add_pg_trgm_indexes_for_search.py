"""add pg_trgm indexes for search

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-03-19 17:51:00.000000

タイトル・ファイル名・著者名・タグ名への LIKE/ILIKE 検索を高速化するため、
PostgreSQL の pg_trgm 拡張を有効にし GIN トライグラムインデックスを追加する。

効果:
- S1-c タイトル検索 / S1-d 全文検索の応答時間を大幅短縮
- '%keyword%' 形式の前後ワイルドカード LIKE が B-tree インデックスを使えない問題を解消
- books.library_id / books.add_date への B-tree インデックスも追加（書籍一覧高速化）
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = 'b2c3d4e5f6a7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # pg_trgm 拡張を有効化（既に存在する場合はスキップ）
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    # books テーブル: タイトル・ファイル名への GIN トライグラムインデックス
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_books_title_trgm "
        "ON books USING gin (title gin_trgm_ops)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_books_import_file_name_trgm "
        "ON books USING gin (import_file_name gin_trgm_ops)"
    )

    # authors テーブル: 著者名への GIN トライグラムインデックス
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_authors_name_trgm "
        "ON authors USING gin (name gin_trgm_ops)"
    )

    # tags テーブル: タグ名への GIN トライグラムインデックス
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_tags_name_trgm "
        "ON tags USING gin (name gin_trgm_ops)"
    )

    # books テーブル: library_id / add_date への B-tree インデックス（書籍一覧フィルタ・ソート高速化）
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_books_library_id "
        "ON books (library_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_books_add_date "
        "ON books (add_date DESC)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_books_add_date")
    op.execute("DROP INDEX IF EXISTS idx_books_library_id")
    op.execute("DROP INDEX IF EXISTS idx_tags_name_trgm")
    op.execute("DROP INDEX IF EXISTS idx_authors_name_trgm")
    op.execute("DROP INDEX IF EXISTS idx_books_import_file_name_trgm")
    op.execute("DROP INDEX IF EXISTS idx_books_title_trgm")
    # pg_trgm 拡張は他の用途でも使われる可能性があるため DROP しない
