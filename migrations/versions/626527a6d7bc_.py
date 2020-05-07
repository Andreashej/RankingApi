"""empty message

Revision ID: 626527a6d7bc
Revises: 05c25542d7e6
Create Date: 2019-12-13 10:20:40.488126

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '626527a6d7bc'
down_revision = '05c25542d7e6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key(None, 'competition_ranking_association', 'competitions', ['competition_id'], ['id'])
    op.create_foreign_key(None, 'competition_ranking_association', 'rankinglists', ['rankinglist_id'], ['id'])
    op.alter_column('horses', 'feif_id',
               existing_type=mysql.VARCHAR(length=12),
               nullable=True)
    op.create_foreign_key(None, 'results', 'riders', ['rider_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'results', 'horses', ['horse_id'], ['id'])
    op.create_foreign_key(None, 'results', 'tests', ['test_id'], ['id'])
    op.create_foreign_key(None, 'tests', 'competitions', ['competition_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'tests', type_='foreignkey')
    op.drop_constraint(None, 'results', type_='foreignkey')
    op.drop_constraint(None, 'results', type_='foreignkey')
    op.drop_constraint(None, 'results', type_='foreignkey')
    op.alter_column('horses', 'feif_id',
               existing_type=mysql.VARCHAR(length=12),
               nullable=False)
    op.drop_constraint(None, 'competition_ranking_association', type_='foreignkey')
    op.drop_constraint(None, 'competition_ranking_association', type_='foreignkey')
    # ### end Alembic commands ###
