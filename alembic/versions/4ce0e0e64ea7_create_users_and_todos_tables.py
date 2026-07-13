"""create users and todos tables

Revision ID: 4ce0e0e64ea7
Revises: 
Create Date: 2026-07-13 16:06:18.052264

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4ce0e0e64ea7'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    if 'users' not in existing_tables:
        op.create_table(
            'users',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('email', sa.String(length=255), nullable=False),
            sa.Column('hashed_password', sa.String(length=255), nullable=False),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
        op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    if 'todos' not in existing_tables:
        op.create_table(
            'todos',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('title', sa.String(length=255), nullable=False),
            sa.Column('description', sa.String(length=500), nullable=True),
            sa.Column('completed', sa.Boolean(), nullable=True),
            sa.Column('owner_id', sa.Integer(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
        )

    if 'owner_id' not in {column['name'] for column in inspector.get_columns('todos')}:
        with op.batch_alter_table('todos', schema=None) as batch_op:
            batch_op.add_column(sa.Column('owner_id', sa.Integer(), nullable=True))

    if 'todos' in existing_tables or 'owner_id' in {column['name'] for column in inspector.get_columns('todos')}:
        with op.batch_alter_table('todos', schema=None) as batch_op:
            batch_op.create_foreign_key('fk_todos_owner_id_users', 'users', ['owner_id'], ['id'])
            batch_op.alter_column('owner_id', existing_type=sa.INTEGER(), nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('todos', schema=None) as batch_op:
        batch_op.drop_constraint('fk_todos_owner_id_users', type_='foreignkey')
        batch_op.alter_column('owner_id', existing_type=sa.INTEGER(), nullable=True)

    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_table('todos')
