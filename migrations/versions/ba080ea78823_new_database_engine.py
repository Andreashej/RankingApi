"""new database engine

Revision ID: ba080ea78823
Revises: 5ec815484b82
Create Date: 2020-06-05 17:00:10.127342

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ba080ea78823'
down_revision = '5ec815484b82'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key(None, 'rankinglist_tests', 'rankinglists', ['rankinglist_id'], ['id'])
    op.create_foreign_key(None, 'results', 'horses', ['horse_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'results', 'tests', ['test_id'], ['id'])
    op.create_foreign_key(None, 'results', 'riders', ['rider_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'task', 'competitions', ['competition_id'], ['id'])
    op.create_foreign_key(None, 'tests', 'competitions', ['competition_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'tests', type_='foreignkey')
    op.drop_constraint(None, 'task', type_='foreignkey')
    op.drop_constraint(None, 'results', type_='foreignkey')
    op.drop_constraint(None, 'results', type_='foreignkey')
    op.drop_constraint(None, 'results', type_='foreignkey')
    op.drop_constraint(None, 'rankinglist_tests', type_='foreignkey')
    # ### end Alembic commands ###
