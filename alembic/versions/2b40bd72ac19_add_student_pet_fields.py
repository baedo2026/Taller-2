"""Add fields used by the student and pet CRUD.

Revision ID: 2b40bd72ac19
Revises: 83d63607b53e
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "2b40bd72ac19"
down_revision: Union[str, Sequence[str], None] = "83d63607b53e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "students",
        sa.Column("username", sa.String(length=30), nullable=True),
    )
    op.execute("UPDATE students SET username = 'student_' || id WHERE username IS NULL")
    op.alter_column("students", "username", nullable=False)
    op.create_unique_constraint("uq_students_username", "students", ["username"])
    op.add_column(
        "students",
        sa.Column("age", sa.Integer(), server_default="18", nullable=False),
    )
    op.alter_column("students", "age", server_default=None)
    op.add_column(
        "students",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.add_column(
        "students",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.add_column("pets", sa.Column("age", sa.Integer(), nullable=True))
    op.add_column(
        "pets",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.add_column(
        "pets",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_unique_constraint(
        "uq_pets_owner_id_name", "pets", ["owner_id", "name"]
    )


def downgrade() -> None:
    op.drop_constraint("uq_pets_owner_id_name", "pets", type_="unique")
    op.drop_column("pets", "updated_at")
    op.drop_column("pets", "created_at")
    op.drop_column("pets", "age")
    op.drop_column("students", "updated_at")
    op.drop_column("students", "created_at")
    op.drop_column("students", "age")
    op.drop_constraint("uq_students_username", "students", type_="unique")
    op.drop_column("students", "username")
