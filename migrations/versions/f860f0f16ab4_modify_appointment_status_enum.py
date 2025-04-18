import sqlmodel

"""add new statuses to appointmentstatus
Revision ID: <new_revision_id>
Revises: f860f0f16ab4
Create Date: <current_date>
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "f860f0f16ab4"
down_revision: Union[str, None] = "31f0fc547ca3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Step 1: Drop the existing default constraint
    op.execute("ALTER TABLE appointment ALTER COLUMN status DROP DEFAULT")

    # Step 2: Rename the existing ENUM type to a temporary name
    op.execute("ALTER TYPE appointmentstatus RENAME TO appointmentstatus_old")

    # Step 3: Create the new ENUM type with all existing values plus new ones
    op.execute(
        "CREATE TYPE appointmentstatus AS ENUM ('PENDING', 'VITALS_RECORDED', 'COMPLETED', 'DIAGNOSED', 'CANCELED')"
    )

    # Step 4: Alter the table to use the new ENUM type
    op.execute(
        "ALTER TABLE appointment ALTER COLUMN status TYPE appointmentstatus USING status::text::appointmentstatus"
    )

    # Step 5: Drop the old ENUM type
    op.execute("DROP TYPE appointmentstatus_old")

    # Step 6: Reapply the default and NOT NULL constraints
    op.execute(
        "ALTER TABLE appointment ALTER COLUMN status SET DEFAULT 'PENDING'::appointmentstatus"
    )
    op.execute("ALTER TABLE appointment ALTER COLUMN status SET NOT NULL")


def downgrade():
    # Step 1: Drop the default constraint
    op.execute("ALTER TABLE appointment ALTER COLUMN status DROP DEFAULT")

    # Step 2: Create a temporary ENUM with only the original values
    op.execute(
        "CREATE TYPE appointmentstatus_old AS ENUM ('PENDING', 'VITALS_RECORDED', 'COMPLETED', 'IN_PROGRESS')"
    )

    # Step 3: Update the table to use the old ENUM type, mapping new values
    op.execute(
        """
        ALTER TABLE appointment
        ALTER COLUMN status
        TYPE appointmentstatus_old
        USING CASE
            WHEN status::text = 'NO_SHOW' THEN 'CANCELED'::appointmentstatus_old
            WHEN status::text = 'RESCHEDULED' THEN 'PENDING'::appointmentstatus_old
            ELSE status::text::appointmentstatus_old
        END
        """
    )

    # Step 4: Drop the new ENUM type
    op.execute("DROP TYPE appointmentstatus")

    # Step 5: Rename the temporary ENUM back to the original name
    op.execute("ALTER TYPE appointmentstatus_old RENAME TO appointmentstatus")

    # Step 6: Restore the default and NOT NULL constraints
    op.execute(
        "ALTER TABLE appointment ALTER COLUMN status SET DEFAULT 'PENDING'::appointmentstatus"
    )
    op.execute("ALTER TABLE appointment ALTER COLUMN status SET NOT NULL")
