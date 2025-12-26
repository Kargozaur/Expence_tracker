"""fixing tables

Revision ID: 9c6e2b334913
Revises: d54ab364e023
Create Date: 2025-12-26 20:36:27.026573

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9c6e2b334913"
down_revision: Union[str, Sequence[str], None] = "d54ab364e023"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        INSERT INTO currency (code, name, symbol, is_active) VALUES
        ('USD', 'US Dollar',        '$',   true),
        ('EUR', 'Euro',             '€',   true),
        ('GBP', 'British Pound',    '£',   true),
        ('UAH', 'Ukrainian Hryvnia','₴',   true),
        ('PLN', 'Polish Złoty',     'zł',  true),
        ('JPY', 'Japanese Yen',     '¥',   true),
        ('CAD', 'Canadian Dollar',  'C$',  true),
        ('CHF', 'Swiss Franc',      'Fr',  true)
    """)

    op.execute("""
        INSERT INTO expenses_category (category_name) VALUES
        ('Food & Groceries'),
        ('Transportation'),
        ('Housing & Utilities'),
        ('Entertainment'),
        ('Health'),
        ('Education'),
        ('Shopping'),
        ('Travel'),
        ('Other')

    """)


def downgrade() -> None:
    """Downgrade schema."""
    pass
