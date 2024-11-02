"""Dropped table Application again due to duplicate foreign_id relationship

Revision ID: d40c5dbab85b
Revises: 090f517e7627
Create Date: 2024-11-01 13:25:49.404849

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd40c5dbab85b'
down_revision: Union[str, None] = '090f517e7627'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade():
    # Drop the applications table
    op.drop_table('applications')

def downgrade():
    # Recreate the applications table with its complete structure
    op.create_table(
        'applications',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True, default=sa.text('uuid_generate_v4()'), index=True),
        sa.Column('application_date', sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column('updated_date', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('status', sa.String, server_default='Pending', nullable=False),
        sa.Column('custom_fields', sa.JSON, server_default='{}'),
        sa.Column('program_id', sa.UUID(as_uuid=True), sa.ForeignKey('programs.id')),
        sa.Column('student_id', sa.UUID(as_uuid=True), sa.ForeignKey('students.id')),
        sa.Column('application_type_id', sa.UUID(as_uuid=True), sa.ForeignKey('programs.id')),
        sa.Column('application_type', sa.String(255), nullable=False)
    )