"""tasks

Revision ID: 58eb998defcf
Revises: 1323a33c7b54
Create Date: 2019-12-17 10:36:50.579011

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '58eb998defcf'
down_revision = '1323a33c7b54'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key(None, 'competition_ranking_association', 'rankinglists', ['rankinglist_id'], ['id'])
    op.create_foreign_key(None, 'competition_ranking_association', 'competitions', ['competition_id'], ['id'])
    op.create_foreign_key(None, 'results', 'riders', ['rider_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'results', 'horses', ['horse_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'results', 'tests', ['test_id'], ['id'])
    op.create_foreign_key(None, 'tests', 'competitions', ['competition_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'tests', type_='foreignkey')
    op.drop_constraint(None, 'results', type_='foreignkey')
    op.drop_constraint(None, 'results', type_='foreignkey')
    op.drop_constraint(None, 'results', type_='foreignkey')
    op.drop_constraint(None, 'competition_ranking_association', type_='foreignkey')
    op.drop_constraint(None, 'competition_ranking_association', type_='foreignkey')
    # ### end Alembic commands ###
