"""Modified the transactions table

Revision ID: 29437afc2eac
Revises: 1892b3aacb36
Create Date: 2024-11-06 07:27:44.872062

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '29437afc2eac'
down_revision: Union[str, None] = '1892b3aacb36'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Add new columns
    op.add_column('transactions', sa.Column('title', sa.String(), nullable=False))
    op.add_column('transactions', sa.Column('description', sa.Text(), nullable=False))
    op.add_column('transactions', sa.Column('payment_method', sa.String(), nullable=False, server_default='flutterwave'))
    op.add_column('transactions', sa.Column('receiver_email', sa.String(), nullable=True))
    op.add_column('transactions', sa.Column('receiver_phone', sa.String(), nullable=True))
    op.add_column('transactions', sa.Column('currency', sa.String(), nullable=False, server_default='NGN'))
    op.add_column('transactions', sa.Column('exchange_rate', sa.String(), nullable=True))
    op.add_column('transactions', sa.Column('delivery_method', sa.String(), nullable=True))
    op.add_column('transactions', sa.Column('claim_bank', sa.String(), nullable=True))
    op.add_column('transactions', sa.Column('claim_account', sa.String(), nullable=True))
    op.add_column('transactions', sa.Column('stash', sa.Integer(), nullable=True))
    op.add_column('transactions', sa.Column('student_name', sa.String(), nullable=False, server_default='Student Name'))
    op.add_column('transactions', sa.Column('institution_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('institutions.id'), nullable=True))

    # Update default of existing column 'status' (if only the default is changing)
    op.alter_column('transactions', 'status', server_default='pending')

def downgrade():
    # Remove newly added columns
    op.drop_column('transactions', 'title')
    op.drop_column('transactions', 'description')
    op.drop_column('transactions', 'payment_method')
    op.drop_column('transactions', 'receiver_email')
    op.drop_column('transactions', 'receiver_phone')
    op.drop_column('transactions', 'currency')
    op.drop_column('transactions', 'exchange_rate')
    op.drop_column('transactions', 'delivery_method')
    op.drop_column('transactions', 'claim_bank')
    op.drop_column('transactions', 'claim_account')
    op.drop_column('transactions', 'stash')
    op.drop_column('transactions', 'student_name')
    op.drop_column('transactions', 'institution_id')

    # Revert the default of 'status' column if changed
    op.alter_column('transactions', 'status', server_default='Completed')