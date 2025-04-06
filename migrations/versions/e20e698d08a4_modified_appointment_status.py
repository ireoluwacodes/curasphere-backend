import sqlmodel

"""modified appointment status

Revision ID: e20e698d08a4
Revises: b4b799c2ba6c
Create Date: 2025-04-06 17:55:14.699316

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e20e698d08a4"
down_revision: Union[str, None] = "b4b799c2ba6c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# In your migration file (e20e698d08a4_modified_appointment_status.py)


def upgrade():
    # Step 1: Create the enum type (you've already done this)
    op.execute(
        "CREATE TYPE appointmentstatus AS ENUM ('PENDING', 'IN_PROGRESS', 'VITALS_RECORDED', 'COMPLETED')"
    )

    # Step 2: Update existing data to match enum values case exactly
    op.execute(
        "UPDATE appointment SET status = 'PENDING' WHERE status = 'pending'"
    )
    # Add similar statements for other values if needed

    # Step 3: Alter the column with explicit USING clause
    op.execute(
        "ALTER TABLE appointment ALTER COLUMN status TYPE appointmentstatus USING status::appointmentstatus"
    )

    # Step 4: Set the default value and NOT NULL constraint if needed
    op.execute(
        "ALTER TABLE appointment ALTER COLUMN status SET DEFAULT 'PENDING'::appointmentstatus"
    )
    op.execute("ALTER TABLE appointment ALTER COLUMN status SET NOT NULL")


def downgrade():
    # Convert back to VARCHAR
    op.execute(
        "ALTER TABLE appointment ALTER COLUMN status TYPE VARCHAR USING status::VARCHAR"
    )

    # Drop the enum type
    op.execute("DROP TYPE appointmentstatus")
