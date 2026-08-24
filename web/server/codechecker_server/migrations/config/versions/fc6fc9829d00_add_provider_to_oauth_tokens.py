"""
add provider to oauth tokens

Revision ID: fc6fc9829d00
Revises:     5e1501dfd333
Create Date: 2026-08-24 23:28:10.440094
"""

from logging import getLogger

from alembic import op
import sqlalchemy as sa

# Revision identifiers, used by Alembic.
revision = 'fc6fc9829d00'
down_revision = '5e1501dfd333'
branch_labels = None
depends_on = None


def upgrade():
    LOG = getLogger("migration/config")
    # Existing rows predate this column and have no known provider, so
    # leave it nullable for them -- the server treats a NULL provider as
    # "not silently refreshable" and falls back to a normal re-login.
    op.add_column(
        'oauth_tokens',
        sa.Column('provider', sa.String(), nullable=True))


def downgrade():
    LOG = getLogger("migration/config")
    op.drop_column('oauth_tokens', 'provider')
