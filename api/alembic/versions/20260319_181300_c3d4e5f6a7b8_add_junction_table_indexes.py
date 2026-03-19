"""add junction table indexes

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-03-19 18:13:00.000000

authorsソート（派生テーブルJOIN）と全文検索（ILIKE + JOIN）を高速化するため、
中間テーブル（book_to_author / tag_to_book）にインデックスを追加する。

PostgreSQLはForeignKey制約に対して自動的にインデックスを作成しないため、
JOIN/WHERE で頻繁に使われる外部キーカラムには明示的なインデックスが必要。

効果:
- authorsソートの派生サブクエリ (GROUP BY books_to_authors.book_uuid) が高速化
- full_text検索の outerjoin(BookModel.authors / tags) が高速化
- author_like / author_is_favorite フィルタの JOIN も高速化
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = 'c3d4e5f6a7b8'
down_revision = 'b2c3d4e5f6a7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # book_to_author 中間テーブル: 書籍→著者のJOIN/GROUP BY を高速化
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_book_to_author_book_uuid "
        "ON book_to_author (book_uuid)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_book_to_author_author_id "
        "ON book_to_author (author_id)"
    )

    # tag_to_book 中間テーブル: 書籍→タグのJOIN を高速化
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_tag_to_book_book_uuid "
        "ON tag_to_book (book_uuid)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_tag_to_book_tags_id "
        "ON tag_to_book (tags_id)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_tag_to_book_tags_id")
    op.execute("DROP INDEX IF EXISTS idx_tag_to_book_book_uuid")
    op.execute("DROP INDEX IF EXISTS idx_book_to_author_author_id")
    op.execute("DROP INDEX IF EXISTS idx_book_to_author_book_uuid")
