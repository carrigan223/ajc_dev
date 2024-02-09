"""create messages table

Revision ID: b3df1e5efd62
Revises: f229b75c5f0b
Create Date: 2024-02-08 12:37:56.685383

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b3df1e5efd62'
down_revision: Union[str, None] = 'f229b75c5f0b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'chat_messages',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), server_onupdate=sa.func.now()),
    )


def downgrade():
    op.drop_table('chat_messages')
