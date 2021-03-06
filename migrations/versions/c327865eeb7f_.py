"""empty message

Revision ID: c327865eeb7f
Revises: 626527a6d7bc
Create Date: 2019-12-13 10:22:37.044248

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c327865eeb7f'
down_revision = '626527a6d7bc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('horses',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('feif_id', sa.String(length=12), nullable=True),
    sa.Column('horse_name', sa.String(length=250), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('feif_id')
    )
    op.create_foreign_key(None, 'competition_ranking_association', 'rankinglists', ['rankinglist_id'], ['id'])
    op.create_foreign_key(None, 'competition_ranking_association', 'competitions', ['competition_id'], ['id'])
    op.create_foreign_key(None, 'results', 'tests', ['test_id'], ['id'])
    op.create_foreign_key(None, 'results', 'horses', ['horse_id'], ['id'])
    op.create_foreign_key(None, 'results', 'riders', ['rider_id'], ['id'], ondelete='CASCADE')
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
    op.drop_table('horses')
    # ### end Alembic commands ###
