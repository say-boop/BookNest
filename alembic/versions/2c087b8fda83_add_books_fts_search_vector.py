"""add_books_fts_search_vector

Revision ID: 2c087b8fda83
Revises: 10beeeb982b7
Create Date: 2026-10-28 13:55:43.887557

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '2c087b8fda83'
down_revision: Union[str, Sequence[str], None] = '10beeeb982b7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'books',
        sa.Column(
            'search_vector',
            postgresql.TSVECTOR(),
            sa.Computed(
                "setweight(to_tsvector('russian', coalesce(title, '')), 'A') || " \
                "setweight(to_tsvector('russian', coalesce(author, '')), 'A') || " \
                "setweight(to_tsvector('russian', coalesce(note, '')), 'A')",
                persisted=True
            ),
            nullable=True
        )
    )

    op.create_index(
        'idx_books_search_vector',
        'books',
        ['search_vector'],
        unique=False,
        postgresql_using="gin"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('idx_books_search_vector', table_name='books', postgresql_unig='gin')
    op.drop_column('books', 'search_vector')