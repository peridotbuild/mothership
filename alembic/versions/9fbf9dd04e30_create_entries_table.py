"""create entries table

Revision ID: 9fbf9dd04e30
Revises: 
Create Date: 2023-06-26 05:24:50.925093

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9fbf9dd04e30"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "entries",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("entry_uuid", sa.String(), nullable=False),
        sa.Column("package_name", sa.String(), nullable=False),
        sa.Column("package_version", sa.String(), nullable=False),
        sa.Column("package_release", sa.String(), nullable=False),
        sa.Column("package_epoch", sa.String(), nullable=False),
        sa.Column("os_release", sa.String(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("entries")
