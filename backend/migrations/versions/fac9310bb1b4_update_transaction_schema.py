"""update transaction schema

Revision ID: fac9310bb1b4
Revises: add_name_and_username_to_user
Create Date: 2025-07-21 21:59:47.746520

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = 'fac9310bb1b4'
down_revision = 'add_name_and_username_to_user'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    insp = inspect(bind)
    cols = {c['name'] for c in insp.get_columns('transaction')}
    with op.batch_alter_table('transaction') as batch_op:
        if 'date' in cols and 'transaction_date' not in cols:
            batch_op.alter_column('date', new_column_name='transaction_date')
        elif 'transaction_date' not in cols:
            batch_op.add_column(sa.Column('transaction_date', sa.Date()))

        if 'posting_date' not in cols:
            batch_op.add_column(sa.Column('posting_date', sa.Date()))
        if 'original_amount' not in cols:
            batch_op.add_column(sa.Column('original_amount', sa.Numeric(10, 2)))
        if 'vat' not in cols:
            batch_op.add_column(sa.Column('vat', sa.Numeric(10, 2)))
        if 'amount' in cols and 'total_amount' not in cols:
            batch_op.alter_column('amount', new_column_name='total_amount')
        elif 'total_amount' not in cols:
            batch_op.add_column(sa.Column('total_amount', sa.Numeric(10, 2)))
        if 'currency' not in cols:
            batch_op.add_column(sa.Column('currency', sa.String(10)))
        if 'is_credit' not in cols:
            batch_op.add_column(sa.Column('is_credit', sa.Boolean(), nullable=True))
        if 'cardholder_name' not in cols:
            batch_op.add_column(sa.Column('cardholder_name', sa.String(100)))
        if 'source_file' not in cols:
            batch_op.add_column(sa.Column('source_file', sa.String(200)))
        if 'cardholder_id' not in cols:
            batch_op.add_column(sa.Column('cardholder_id', sa.Integer()))

        if 'date' in cols and 'transaction_date' in cols:
            batch_op.drop_column('date')
        if 'amount' in cols and 'total_amount' in cols:
            batch_op.drop_column('amount')


def downgrade():
    bind = op.get_bind()
    insp = inspect(bind)
    cols = {c['name'] for c in insp.get_columns('transaction')}
    with op.batch_alter_table('transaction') as batch_op:
        if 'transaction_date' in cols and 'date' not in cols:
            batch_op.alter_column('transaction_date', new_column_name='date')
        if 'posting_date' in cols:
            batch_op.drop_column('posting_date')
        if 'original_amount' in cols:
            batch_op.drop_column('original_amount')
        if 'vat' in cols:
            batch_op.drop_column('vat')
        if 'total_amount' in cols and 'amount' not in cols:
            batch_op.alter_column('total_amount', new_column_name='amount')
        if 'currency' in cols:
            batch_op.drop_column('currency')
        if 'is_credit' in cols:
            batch_op.drop_column('is_credit')
        if 'cardholder_name' in cols:
            batch_op.drop_column('cardholder_name')
        if 'source_file' in cols:
            batch_op.drop_column('source_file')
        if 'cardholder_id' in cols:
            batch_op.drop_column('cardholder_id')
