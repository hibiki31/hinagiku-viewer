"""add_tasks_table

Revision ID: 59a15d1f226d
Revises: 249b14ac2a94
Create Date: 2026-02-10 20:15:42.343399

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '59a15d1f226d'
down_revision = '249b14ac2a94'
branch_labels = None
depends_on = None


def upgrade():
    # tasksテーブルを作成
    op.create_table(
        'tasks',
        sa.Column('id', sa.String(), nullable=False, comment='タスクID（UUID）'),
        sa.Column('task_type', sa.String(length=50), nullable=False, comment='タスク種別: load, sim_all, export等'),
        sa.Column('status', sa.String(length=20), nullable=False, comment='ステータス: pending, running, completed, failed, cancelled'),
        sa.Column('progress', sa.Integer(), server_default='0', comment='進捗率 0-100'),
        sa.Column('current_item', sa.Integer(), server_default='0', comment='処理済み件数'),
        sa.Column('total_items', sa.Integer(), nullable=True, comment='全体件数'),
        sa.Column('current_step', sa.String(length=200), nullable=True, comment='現在のステップ: 初期化中、ハッシュ計算中等'),
        sa.Column('message', sa.String(length=500), nullable=True, comment='現在の処理内容メッセージ'),
        sa.Column('error_message', sa.String(length=1000), nullable=True, comment='エラー詳細メッセージ'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False, comment='作成日時'),
        sa.Column('started_at', sa.DateTime(), nullable=True, comment='開始日時'),
        sa.Column('completed_at', sa.DateTime(), nullable=True, comment='完了日時'),
        sa.Column('user_id', sa.String(), nullable=True, comment='実行ユーザー'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], onupdate='CASCADE', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # インデックス作成
    op.create_index('idx_tasks_task_type', 'tasks', ['task_type'])
    op.create_index('idx_tasks_status', 'tasks', ['status'])
    op.create_index('idx_tasks_status_created', 'tasks', ['status', 'created_at'])
    op.create_index('idx_tasks_user_status', 'tasks', ['user_id', 'status'])


def downgrade():
    # インデックス削除
    op.drop_index('idx_tasks_user_status', 'tasks')
    op.drop_index('idx_tasks_status_created', 'tasks')
    op.drop_index('idx_tasks_status', 'tasks')
    op.drop_index('idx_tasks_task_type', 'tasks')
    
    # テーブル削除
    op.drop_table('tasks')
