"""add bigscreen routes

Revision ID: 8226fdbdc022
Revises: 6bef99e14741
Create Date: 2022-05-27 15:39:28.890080

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8226fdbdc022'
down_revision = '6bef99e14741'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('bigscreen_routes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('priority', sa.Integer(), nullable=True),
    sa.Column('screen_group_id', sa.Integer(), nullable=True),
    sa.Column('competition_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['competition_id'], ['competitions.id'], ),
    sa.ForeignKeyConstraint(['screen_group_id'], ['screengroups.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('bigscreen_template_routes',
    sa.Column('route_id', sa.Integer(), nullable=False),
    sa.Column('template_name', sa.String(length=50), nullable=False),
    sa.ForeignKeyConstraint(['route_id'], ['bigscreen_routes.id'], ),
    sa.PrimaryKeyConstraint('route_id', 'template_name')
    )
    op.create_table('test_bigscreenroutes',
    sa.Column('route_id', sa.Integer(), nullable=False),
    sa.Column('test_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['route_id'], ['bigscreen_routes.id'], ),
    sa.ForeignKeyConstraint(['test_id'], ['tests.id'], ),
    sa.PrimaryKeyConstraint('route_id', 'test_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('test_bigscreenroutes')
    op.drop_table('bigscreen_template_routes')
    op.drop_table('bigscreen_routes')
    # ### end Alembic commands ###