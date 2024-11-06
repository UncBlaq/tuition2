"""Modified intitution.id relationship to the correct version institutions.id

Revision ID: 44b3b3e8a9d7
Revises: 29437afc2eac
Create Date: 2024-11-06 08:28:23.448575

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '44b3b3e8a9d7'
down_revision: Union[str, None] = '29437afc2eac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Drop the old foreign key constraint on institution_id referencing institution.id
    op.drop_constraint('transactions_institution_id_fkey', 'transactions', type_='foreignkey')
    
    # Add a new foreign key constraint on institution_id referencing institutions.id
    op.create_foreign_key(
        'transactions_institution_id_fkey',
        'transactions',
        'institutions',
        ['institution_id'],
        ['id']
    )

def downgrade():
    # Drop the new foreign key constraint on institution_id referencing institutions.id
    op.drop_constraint('transactions_institution_id_fkey', 'transactions', type_='foreignkey')
    
    # Add back the old foreign key constraint on institution_id referencing institution.id
    op.create_foreign_key(
        'transactions_institution_id_fkey',
        'transactions',
        'institution',
        ['institution_id'],
        ['id']
    )