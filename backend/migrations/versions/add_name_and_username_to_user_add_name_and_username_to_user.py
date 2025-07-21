"""Add name and username to User

Revision ID: add_name_and_username_to_user
Revises: 
Create Date: 2025-07-21 19:02:00.814037

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_name_and_username_to_user'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('user') as batch_op:
        batch_op.add_column(sa.Column('name', sa.String(length=80), nullable=True))
        batch_op.add_column(sa.Column('username', sa.String(length=80), nullable=True))
        batch_op.create_unique_constraint('uq_user_username', ['username'])


def downgrade():
    with op.batch_alter_table('user') as batch_op:
        batch_op.drop_constraint('uq_user_username', type_='unique')
        batch_op.drop_column('username')
        batch_op.drop_column('name')
