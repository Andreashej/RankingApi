"""add osd to screen group

Revision ID: 2382610f9cd0
Revises: 8d35237375e9
Create Date: 2022-03-01 22:14:47.513039

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2382610f9cd0'
down_revision = '8d35237375e9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('screengroups', sa.Column('show_osd', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('screengroups', 'show_osd')
    # ### end Alembic commands ###