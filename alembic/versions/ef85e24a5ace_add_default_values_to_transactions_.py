"""Add default values to transactions columns

Revision ID: ef85e24a5ace
Revises: a00ec6de2ea3
Create Date: 2024-11-06 11:28:05.996082

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'ef85e24a5ace'
down_revision: Union[str, None] = 'a00ec6de2ea3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Add default values for nullable columns that did not have a default value
    op.alter_column('transactions', 'receiver_email', existing_type=sa.String(), nullable=True, server_default=None)
    op.alter_column('transactions', 'receiver_phone', existing_type=sa.String(), nullable=True, server_default=None)
    op.alter_column('transactions', 'delivery_method', existing_type=sa.String(), nullable=True, server_default=None)
    op.alter_column('transactions', 'claim_bank', existing_type=sa.String(), nullable=True, server_default=None)
    op.alter_column('transactions', 'claim_account', existing_type=sa.String(), nullable=True, server_default=None)
    op.alter_column('transactions', 'stash', existing_type=sa.Integer(), nullable=True, server_default=None)



def downgrade():
    # Revert the changes made to the columns
    op.alter_column('transactions', 'receiver_email', existing_type=sa.String(), nullable=True, server_default=None)
    op.alter_column('transactions', 'receiver_phone', existing_type=sa.String(), nullable=True, server_default=None)
    op.alter_column('transactions', 'delivery_method', existing_type=sa.String(), nullable=True, server_default=None)
    op.alter_column('transactions', 'claim_bank', existing_type=sa.String(), nullable=True, server_default=None)
    op.alter_column('transactions', 'claim_account', existing_type=sa.String(), nullable=True, server_default=None)
    op.alter_column('transactions', 'stash', existing_type=sa.Integer(), nullable=True, server_default=None)

