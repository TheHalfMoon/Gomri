"""add evidence narrative to presentations

Revision ID: 9a3c1f7b2d40
Revises: 026c0ba8b35c
Create Date: 2026-10-22 00:00:00.000000

The W3 grain persists two things on a presentation so that every citation can
be revalidated at export time, long after generation:

- ``narrative`` — the evidence-bound NarrativeIR, whose sections carry the
  citation locators and the evidence status of each node;
- ``source_ir`` — the source IR those locators resolve against.

Both are nullable. A presentation generated without evidence keeps the exact
behaviour it had before this revision.
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = "9a3c1f7b2d40"
down_revision: str | None = "026c0ba8b35c"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _has_column(table_name: str, column_name: str) -> bool:
    inspector = sa.inspect(op.get_bind())
    if table_name not in inspector.get_table_names():
        return False
    return column_name in {column["name"] for column in inspector.get_columns(table_name)}


def upgrade() -> None:
    if not _has_column("presentations", "narrative"):
        op.add_column("presentations", sa.Column("narrative", sa.JSON(), nullable=True))
    if not _has_column("presentations", "source_ir"):
        op.add_column("presentations", sa.Column("source_ir", sa.JSON(), nullable=True))


def downgrade() -> None:
    if _has_column("presentations", "source_ir"):
        op.drop_column("presentations", "source_ir")
    if _has_column("presentations", "narrative"):
        op.drop_column("presentations", "narrative")
