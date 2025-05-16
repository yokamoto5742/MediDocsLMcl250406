"""初期スキーマとdocument_typeカラムの追加

Revision ID: 001_initial_schema
Revises: 
Create Date: 2025-05-15

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 既存テーブルが存在するか確認し、存在しなければ作成
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    
    # usersテーブルのチェックと作成
    if 'users' not in inspector.get_table_names():
        op.create_table('users',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('username', sa.String(length=100), nullable=False),
            sa.Column('password', sa.LargeBinary(), nullable=False),
            sa.Column('is_admin', sa.Boolean(), nullable=True, default=False),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('username')
        )
    
    # departmentsテーブルのチェックと作成
    if 'departments' not in inspector.get_table_names():
        op.create_table('departments',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=100), nullable=False),
            sa.Column('order_index', sa.Integer(), nullable=False),
            sa.Column('default_model', sa.String(length=50), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('name')
        )
    
    # promptsテーブルのチェックと作成/修正
    if 'prompts' not in inspector.get_table_names():
        op.create_table('prompts',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('department', sa.String(length=100), nullable=False),
            sa.Column('document_type', sa.String(length=100), nullable=False),
            sa.Column('doctor', sa.String(length=100), nullable=False),
            sa.Column('name', sa.String(length=100), nullable=False),
            sa.Column('content', sa.Text(), nullable=False),
            sa.Column('is_default', sa.Boolean(), nullable=True, default=False),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('department', 'document_type', 'doctor', 'name', name='unique_prompt')
        )
    else:
        # promptsテーブルが存在する場合、document_typeカラムの存在確認
        columns = [column['name'] for column in inspector.get_columns('prompts')]
        if 'document_type' not in columns:
            # document_typeカラムを追加
            op.add_column('prompts', sa.Column('document_type', sa.String(length=100), nullable=True))
            # デフォルト値として'退院時サマリ'を設定
            op.execute("UPDATE prompts SET document_type = '退院時サマリ' WHERE document_type IS NULL")
            # NULL制約を追加
            op.alter_column('prompts', 'document_type', nullable=False)
            
            # 制約の修正（ユニーク制約の更新）
            try:
                op.drop_constraint('unique_prompt', 'prompts', type_='unique')
            except:
                pass  # 制約が存在しない場合
            op.create_unique_constraint('unique_prompt', 'prompts', ['department', 'document_type', 'doctor', 'name'])
    
    # summary_usageテーブルのチェックと作成
    if 'summary_usage' not in inspector.get_table_names():
        op.create_table('summary_usage',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('date', sa.DateTime(timezone=True), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.Column('app_type', sa.String(length=50), nullable=True),
            sa.Column('document_name', sa.String(length=100), nullable=True),
            sa.Column('model_detail', sa.String(length=100), nullable=True),
            sa.Column('department', sa.String(length=100), nullable=True),
            sa.Column('input_tokens', sa.Integer(), nullable=True),
            sa.Column('output_tokens', sa.Integer(), nullable=True),
            sa.Column('total_tokens', sa.Integer(), nullable=True),
            sa.Column('processing_time', sa.Integer(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
    
    # app_settingsテーブルのチェックと作成
    if 'app_settings' not in inspector.get_table_names():
        op.create_table('app_settings',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('setting_id', sa.String(length=100), nullable=False),
            sa.Column('selected_department', sa.String(length=100), nullable=True),
            sa.Column('selected_model', sa.String(length=50), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('setting_id')
        )
    
    # document_typesテーブルのチェックと作成
    if 'document_types' not in inspector.get_table_names():
        op.create_table('document_types',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=100), nullable=False),
            sa.Column('order_index', sa.Integer(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('name')
        )


def downgrade() -> None:
    # document_typeカラムを削除
    op.drop_constraint('unique_prompt', 'prompts', type_='unique')
    op.drop_column('prompts', 'document_type')
    op.create_unique_constraint('unique_prompt', 'prompts', ['department', 'doctor', 'name'])
    
    # 注意: 初期スキーマのダウングレードはここでは実装しません
    # 既存データを消去してしまう危険性があるため