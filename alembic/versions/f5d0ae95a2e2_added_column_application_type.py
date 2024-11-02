"""added column application type

Revision ID: f5d0ae95a2e2
Revises: 755c04eda90e
Create Date: 2024-11-01 09:38:44.511693

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f5d0ae95a2e2'
down_revision: Union[str, None] = '755c04eda90e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Add 'application_type' column to the 'applications' table
    op.add_column(
        'applications',
        sa.Column('application_type', sa.String(length=255), nullable=False)
    )

def downgrade() -> None:
    # Remove 'application_type' column on downgrade
    op.drop_column('applications', 'application_type')