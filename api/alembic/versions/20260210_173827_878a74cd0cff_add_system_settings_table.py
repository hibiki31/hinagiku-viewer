"""add_system_settings_table

Revision ID: 878a74cd0cff
Revises: 40f414b33f9d
Create Date: 2026-02-10 17:38:27.457612

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '878a74cd0cff'
down_revision = '40f414b33f9d'
branch_labels = None
depends_on = None


def upgrade():
    # system_settings テーブルを作成
    op.create_table(
        'system_settings',
        sa.Column('key', sa.String(length=255), nullable=False, comment='設定キー'),
        sa.Column('value', sa.String(length=1000), nullable=False, comment='設定値（文字列として保存）'),
        sa.Column('data_type', sa.String(length=50), nullable=False, comment='データ型: int, float, bool, string, json'),
        sa.Column('description', sa.String(length=500), nullable=True, comment='設定の説明'),
        sa.Column('category', sa.String(length=100), nullable=True, comment='カテゴリ: system, security, task, thumbnail等'),
        sa.Column('is_public', sa.Boolean(), nullable=False, server_default='false', comment='非管理者も取得可能か'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), comment='更新日時'),
        sa.Column('updated_by', sa.String(), nullable=True, comment='更新者'),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], onupdate='CASCADE', ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('key')
    )
    
    # インデックス作成
    op.create_index('idx_system_settings_category', 'system_settings', ['category'])
    op.create_index('idx_system_settings_is_public', 'system_settings', ['is_public'])
    
    # デフォルトデータを挿入
    op.execute("""
        INSERT INTO system_settings (key, value, data_type, description, category, is_public) VALUES
        ('thumbnail_quality', '85', 'int', 'サムネイル画像の品質 (0-100)', 'thumbnail', false),
        ('thumbnail_max_size', '800', 'int', 'サムネイル最大サイズ (px)', 'thumbnail', false),
        ('task_parallel_limit', '4', 'int', 'タスク並列実行数', 'task', false),
        ('task_timeout_minutes', '60', 'int', 'タスクタイムアウト時間 (分)', 'task', false),
        ('token_expire_days', '30', 'int', 'トークン有効期限 (日)', 'security', false),
        ('max_login_attempts', '5', 'int', '最大ログイン試行回数', 'security', false),
        ('maintenance_mode', 'false', 'bool', 'メンテナンスモード', 'system', true),
        ('allow_new_user_registration', 'true', 'bool', '新規ユーザー登録を許可', 'system', true)
    """)


def downgrade():
    # インデックス削除
    op.drop_index('idx_system_settings_is_public', 'system_settings')
    op.drop_index('idx_system_settings_category', 'system_settings')
    
    # テーブル削除
    op.drop_table('system_settings')
