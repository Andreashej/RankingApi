"""remove rider_id and horse_id columns from result

Revision ID: 2513af2fae72
Revises: 17645b7c6ee4
Create Date: 2021-12-01 20:29:02.862160

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '2513af2fae72'
down_revision = '17645b7c6ee4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('results_cache', 'horse_id')
    op.drop_column('results_cache', 'rider_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('results_cache', sa.Column('rider_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.add_column('results_cache', sa.Column('horse_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
