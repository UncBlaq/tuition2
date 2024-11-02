"""Made column edits to the application table

Revision ID: 755c04eda90e
Revises: 6f7a5342c3cd
Create Date: 2024-11-01 09:11:50.516191

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '755c04eda90e'
down_revision: Union[str, None] = '6f7a5342c3cd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Remove 'application_type' column
    op.drop_column('applications', 'application_type')
    
    # Add 'custom_fields' JSON column with a default empty dictionary
    op.add_column(
        'applications',
        sa.Column('custom_fields', postgresql.JSON, server_default=sa.text("'{}'"), nullable=False)
    )
    
    # Rename 'program_id' to 'application_type_id'
    op.alter_column('applications', 'program_id', new_column_name='application_type_id', type_= postgresql.UUID)


def downgrade() -> None:
    # Revert the column name change on downgrade
    op.alter_column('applications', 'application_type_id', new_column_name='program_id', type_= postgresql.UUID)
    
    # Remove the 'custom_fields' column on downgrade
    op.drop_column('applications', 'custom_fields')
    
    # Re-add 'application_type' column
    op.add_column(
        'applications',
        sa.Column('application_type', sa.String, nullable=False)
    )