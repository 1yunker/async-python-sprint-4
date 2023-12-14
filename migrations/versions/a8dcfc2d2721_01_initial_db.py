"""01_initial-db

Revision ID: a8dcfc2d2721
Revises: 
Create Date: 2023-12-14 23:08:49.811593

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a8dcfc2d2721'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('urls',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('original_url', sa.String(), nullable=True),
    sa.Column('short_url', sa.String(), nullable=True),
    sa.Column('short_id', sa.String(), nullable=True),
    sa.Column('clicks', sa.Integer(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_urls_original_url'), 'urls', ['original_url'], unique=False)
    op.create_index(op.f('ix_urls_short_id'), 'urls', ['short_id'], unique=True)
    op.create_index(op.f('ix_urls_short_url'), 'urls', ['short_url'], unique=True)
    op.create_table('clicks',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('url_id', sa.Integer(), nullable=True),
    sa.Column('user_agent', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['url_id'], ['urls.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('clicks')
    op.drop_index(op.f('ix_urls_short_url'), table_name='urls')
    op.drop_index(op.f('ix_urls_short_id'), table_name='urls')
    op.drop_index(op.f('ix_urls_original_url'), table_name='urls')
    op.drop_table('urls')
    # ### end Alembic commands ###