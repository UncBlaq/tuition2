"""Second and Proper addition of Application table

Revision ID: 1892b3aacb36
Revises: d40c5dbab85b
Create Date: 2024-11-01 13:34:08.333274

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '1892b3aacb36'
down_revision: Union[str, None] = 'd40c5dbab85b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Re-create the applications table with updated columns and relationships
    op.create_table(
        'applications',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('application_date', sa.TIMESTAMP(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_date', sa.TIMESTAMP(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('status', sa.VARCHAR(), server_default='Pending', nullable=False),
        sa.Column('custom_fields', sa.JSON(), server_default=sa.text("'{}'"), nullable=True),  # Use server_default for JSON
        sa.Column('student_id', sa.UUID(as_uuid=True), sa.ForeignKey('students.id'), nullable=False),
        sa.Column('application_type_id', sa.UUID(as_uuid=True), sa.ForeignKey('programs.id'), nullable=True),
        sa.Column('application_type', sa.VARCHAR(255), nullable=False),
    )

def downgrade():
    # Drop the applications table if needed for downgrade
    op.drop_table('applications')
