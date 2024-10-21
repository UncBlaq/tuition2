"""Added program_level and category relationship to programs
table

Revision ID: a0f70cce2993
Revises: 
Create Date: 2024-10-17 04:56:29.611772

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a0f70cce2993'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Use string literal for 'server_default'
    op.add_column('programs', sa.Column('program_level', sa.String(), nullable=False, server_default='undergraduate'))

def downgrade() -> None:
    # Drop the 'program_level' column on downgrade
    op.drop_column('programs', 'program_level')


