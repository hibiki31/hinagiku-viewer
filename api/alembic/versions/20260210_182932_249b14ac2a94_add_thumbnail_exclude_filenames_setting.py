"""add_thumbnail_exclude_filenames_setting

Revision ID: 249b14ac2a94
Revises: 878a74cd0cff
Create Date: 2026-02-10 18:29:32.680767

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '249b14ac2a94'
down_revision = '878a74cd0cff'
branch_labels = None
depends_on = None


def upgrade():
    # サムネイル除外ファイル名設定を追加
    op.execute("""
        INSERT INTO system_settings (key, value, data_type, description, category, is_public) VALUES
        ('thumbnail_exclude_filenames', 'Sample.jpg', 'string', 'サムネイル作成時に除外するファイル名（カンマ区切り）', 'thumbnail', false)
    """)


def downgrade():
    # サムネイル除外ファイル名設定を削除
    op.execute("""
        DELETE FROM system_settings WHERE key = 'thumbnail_exclude_filenames'
    """)
