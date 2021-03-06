"""ondelete cascade for results cache

Revision ID: 91e86031f915
Revises: 72e00172562e
Create Date: 2020-06-06 13:08:15.671543

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '91e86031f915'
down_revision = '72e00172562e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('horse_results_ibfk_1', 'horse_results', type_='foreignkey')
    op.drop_constraint('horse_results_ibfk_2', 'horse_results', type_='foreignkey')
    op.create_foreign_key(None, 'horse_results', 'results_cache', ['result_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'horse_results', 'horses', ['horse_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('rider_results_ibfk_1', 'rider_results', type_='foreignkey')
    op.drop_constraint('rider_results_ibfk_2', 'rider_results', type_='foreignkey')
    op.create_foreign_key(None, 'rider_results', 'riders', ['rider_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'rider_results', 'results_cache', ['result_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'rider_results', type_='foreignkey')
    op.drop_constraint(None, 'rider_results', type_='foreignkey')
    op.create_foreign_key('rider_results_ibfk_2', 'rider_results', 'riders', ['rider_id'], ['id'])
    op.create_foreign_key('rider_results_ibfk_1', 'rider_results', 'results_cache', ['result_id'], ['id'])
    op.drop_constraint(None, 'horse_results', type_='foreignkey')
    op.drop_constraint(None, 'horse_results', type_='foreignkey')
    op.create_foreign_key('horse_results_ibfk_2', 'horse_results', 'horses', ['horse_id'], ['id'])
    op.create_foreign_key('horse_results_ibfk_1', 'horse_results', 'results_cache', ['result_id'], ['id'])
    # ### end Alembic commands ###
