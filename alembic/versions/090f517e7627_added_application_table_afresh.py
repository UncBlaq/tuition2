"""Added Application table afresh

Revision ID: 090f517e7627
Revises: 48e80ea2d492
Create Date: 2024-11-01 11:33:35.574143

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '090f517e7627'
down_revision: Union[str, None] = '48e80ea2d492'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

import uuid


def upgrade():
    # Re-create the applications table with updated columns and relationships
    op.create_table(
        'applications',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('application_date', sa.TIMESTAMP(), nullable=True),
        sa.Column('updated_date', sa.TIMESTAMP(), nullable=True),
        sa.Column('status', sa.VARCHAR(), nullable=True),
        sa.Column('custom_fields', sa.JSON(), nullable=True),
        sa.Column('program_id', sa.UUID(), nullable=False),  # Change to UUID
        sa.Column('student_id', sa.UUID(), nullable=False),
        sa.Column('application_type_id', sa.UUID(), nullable=True),
        sa.Column('application_type', sa.VARCHAR(255), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['program_id'], ['programs.id']),
        sa.ForeignKeyConstraint(['student_id'], ['students.id']),
        sa.ForeignKeyConstraint(['application_type_id'], ['programs.id'])
    )

def downgrade():
    # Drop the applications table again if needed for downgrade
    op.drop_table('applications')