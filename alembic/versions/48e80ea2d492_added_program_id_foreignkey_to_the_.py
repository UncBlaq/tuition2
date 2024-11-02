"""Dropped the Application Table

Revision ID: 48e80ea2d492
Revises: f5d0ae95a2e2
Create Date: 2024-11-01 10:39:40.882016

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '48e80ea2d492'
down_revision: Union[str, None] = 'f5d0ae95a2e2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None
def upgrade():
    # Drop the applications table
    op.drop_table('applications')

def downgrade():
    # Downgrade logic would ideally re-create the table with its previous structure
    # Placeholder below; modify if you need the exact structure.
    op.create_table(
        'applications',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True),
        sa.Column('application_date', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_date', sa.DateTime, default=sa.func.now()),
        sa.Column('status', sa.String, default='Pending'),
        sa.Column('custom_fields', sa.JSON, default={}),
        sa.Column('student_id', sa.UUID, sa.ForeignKey('students.id')),
        sa.Column('application_type_id', sa.UUID, sa.ForeignKey('programs.id')),
        sa.Column('application_type', sa.String(255), nullable=False),
    )