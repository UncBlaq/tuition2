"""Added an Application table that is related a to a program and and a student making the Application

Revision ID: 6f7a5342c3cd
Revises: ad5f938e993f
Create Date: 2024-10-30 07:12:06.285961

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '6f7a5342c3cd'
down_revision: Union[str, None] = 'ad5f938e993f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    # Create the 'applications' table
    op.create_table(
        'applications',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True, default=sa.text('uuid_generate_v4()'), index=True),
        sa.Column('application_type', sa.String, nullable=False),
        sa.Column('application_date', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_date', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('status', sa.String, default='Pending'),
        sa.Column('student_id', sa.UUID, sa.ForeignKey('students.id'), nullable=True),
        sa.Column('program_id', sa.UUID, sa.ForeignKey('programs.id'), nullable=True),
    )

def downgrade() -> None:
    # Drop the 'applications' table on downgrade
    op.drop_table('applications')
