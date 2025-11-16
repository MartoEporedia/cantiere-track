"""fix attendance notes column type

Revision ID: 20251116_002140
Revises:
Create Date: 2025-11-16 00:21:40.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251116_002140'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Change notes column from integer to text"""
    # First, we need to handle any existing data
    # Since the column was integer but should be text, we'll convert it
    op.execute('ALTER TABLE attendances ALTER COLUMN notes TYPE TEXT USING notes::TEXT')


def downgrade() -> None:
    """Revert notes column back to integer (not recommended)"""
    # This is dangerous if there's actual text data, but provided for completeness
    op.execute('ALTER TABLE attendances ALTER COLUMN notes TYPE INTEGER USING CASE WHEN notes ~ \'^[0-9]+$\' THEN notes::INTEGER ELSE NULL END')
