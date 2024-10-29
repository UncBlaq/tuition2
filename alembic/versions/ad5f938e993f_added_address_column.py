"""Added address column

Revision ID: ad5f938e993f
Revises: 34f7a0eb8b8e
Create Date: 2024-10-29 09:08:52.863561

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'ad5f938e993f'
down_revision: Union[str, None] = '34f7a0eb8b8e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Use string literal for 'server_default'
    op.add_column('students', sa.Column('address', sa.Text, nullable=True))

def downgrade() -> None:
    # Drop the 'program_level' column on downgrade
    op.drop_column('students', 'address')
