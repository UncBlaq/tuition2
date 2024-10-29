"""Added bio and date of birth columns to students and nullable is set to true

Revision ID: 34f7a0eb8b8e
Revises: a0f70cce2993
Create Date: 2024-10-29 07:55:23.437197

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '34f7a0eb8b8e'
down_revision: Union[str, None] = 'a0f70cce2993'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Use string literal for 'server_default'
    op.add_column('students', sa.Column('bio', sa.Text, nullable=True))
    op.add_column('students', sa.Column('date_of_birth', sa.Date, nullable=True))

def downgrade() -> None:
    # Drop the 'program_level' column on downgrade
    op.drop_column('students', 'bio')
    op.drop_column('students', 'date_of_birth')
