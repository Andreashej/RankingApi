"""undo renaming

Revision ID: 5b374a89f873
Revises: 30432516f01f
Create Date: 2021-12-01 18:07:27.833022

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '5b374a89f873'
down_revision = '30432516f01f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # op.drop_index('ix_ranking_results_test_id', table_name='ranking_results')
    # op.drop_table('ranking_results')
    # ### end Alembic commands ###
    pass


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('ranking_results',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('rank', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('mark', mysql.FLOAT(), nullable=True),
    sa.Column('test_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['test_id'], ['rankinglist_tests.id'], name='ranking_results_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset='latin1',
    mysql_engine='InnoDB'
    )
    op.create_index('ix_ranking_results_test_id', 'ranking_results', ['test_id'], unique=False)
    # ### end Alembic commands ###
