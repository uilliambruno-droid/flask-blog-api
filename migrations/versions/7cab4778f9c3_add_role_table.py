"""Add role table

Revision ID: 7cab4778f9c3
Revises: 4b839b563dec
Create Date: 2026-03-06 14:45:38.702804
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "7cab4778f9c3"
down_revision = "4b839b563dec"
branch_labels = None
depends_on = None


FK_USER_ROLE = "fk_user_role_id_role"


def upgrade():
    op.create_table(
        "role",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.add_column(sa.Column("role_id", sa.Integer(), nullable=False))
        batch_op.create_foreign_key(
            FK_USER_ROLE,
            "role",
            ["role_id"],
            ["id"],
        )
        batch_op.drop_column("active")


def downgrade():
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.add_column(sa.Column("active", sa.BOOLEAN(), nullable=False))
        batch_op.drop_constraint(FK_USER_ROLE, type_="foreignkey")
        batch_op.drop_column("role_id")

    op.drop_table("role")
