"""removed last check wf in horses

Revision ID: e29928394640
Revises: 14ff898b5e65
Create Date: 2020-11-15 22:59:22.302451

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'e29928394640'
down_revision = '14ff898b5e65'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('horses', 'last_checked_wf')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('horses', sa.Column('last_checked_wf', mysql.DATETIME(), nullable=True))
    # ### end Alembic commands ###