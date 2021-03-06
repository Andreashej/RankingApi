"""added horses

Revision ID: e34e91e9d00d
Revises: 14c4c09e3837
Create Date: 2019-12-13 09:26:13.434678

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e34e91e9d00d'
down_revision = '14c4c09e3837'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('horses',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('feif_id', sa.String(length=12), nullable=False),
    sa.Column('horse_name', sa.String(length=250), nullable=True),
    sa.PrimaryKeyConstraint('id', 'feif_id')
    )
    op.create_foreign_key(None, 'competition_ranking_association', 'competitions', ['competition_id'], ['id'])
    op.create_foreign_key(None, 'competition_ranking_association', 'rankinglists', ['rankinglist_id'], ['id'])
    op.create_foreign_key(None, 'results', 'riders', ['rider_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'results', 'tests', ['test_id'], ['id'])
    op.create_foreign_key(None, 'tests', 'competitions', ['competition_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'tests', type_='foreignkey')
    op.drop_constraint(None, 'results', type_='foreignkey')
    op.drop_constraint(None, 'results', type_='foreignkey')
    op.drop_constraint(None, 'competition_ranking_association', type_='foreignkey')
    op.drop_constraint(None, 'competition_ranking_association', type_='foreignkey')
    op.drop_table('horses')
    # ### end Alembic commands ###
