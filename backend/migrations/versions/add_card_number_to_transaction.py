"""Add card_number to transaction

Revision ID: add_card_number_to_transaction
Revises: fac9310bb1b4
Create Date: 2025-08-30 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = 'add_card_number_to_transaction'
down_revision = 'fac9310bb1b4'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    insp = inspect(bind)
    cols = {c['name'] for c in insp.get_columns('transaction')}
    with op.batch_alter_table('transaction') as batch_op:
        if 'card_number' not in cols:
            batch_op.add_column(sa.Column('card_number', sa.String(20)))


def downgrade():
    bind = op.get_bind()
    insp = inspect(bind)
    cols = {c['name'] for c in insp.get_columns('transaction')}
    with op.batch_alter_table('transaction') as batch_op:
        if 'card_number' in cols:
            batch_op.drop_column('card_number')
