"""add data structure for elaborate marks

Revision ID: eb483a4baf9f
Revises: 7ecf2a40f23f
Create Date: 2022-01-31 21:21:15.629181

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eb483a4baf9f'
down_revision = '7ecf2a40f23f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('marks',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('mark_type', sa.String(length=4), nullable=True),
    sa.Column('judge_no', sa.Integer(), nullable=True),
    sa.Column('judge_id', sa.String(length=12), nullable=True),
    sa.Column('result_id', sa.Integer(), nullable=True),
    sa.Column('section_mark_id', sa.Integer(), nullable=True),
    sa.Column('red_card', sa.Boolean(), nullable=True),
    sa.Column('yellow_card', sa.Boolean(), nullable=True),
    sa.Column('blue_card', sa.Boolean(), nullable=True),
    sa.Column('mark', sa.Float(), nullable=True),
    sa.Column('is_ok', sa.Boolean(), nullable=True),
    sa.Column('time', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['result_id'], ['results.id'], ),
    sa.ForeignKeyConstraint(['section_mark_id'], ['marks.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('persons', sa.Column('date_of_birth', sa.Date(), nullable=True))
    op.add_column('results', sa.Column('color', sa.String(length=12), nullable=True))
    op.add_column('results', sa.Column('phase', sa.String(length=4), nullable=True))
    op.add_column('results', sa.Column('rider_class', sa.String(length=20), nullable=True))
    op.add_column('results', sa.Column('sta', sa.Integer(), nullable=True))
    op.add_column('results', sa.Column('start_group', sa.Integer(), nullable=True))
    op.add_column('results', sa.Column('timestamp', sa.DateTime(), nullable=True))
    op.add_column('tests', sa.Column('test_name', sa.String(length=20), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tests', 'test_name')
    op.drop_column('results', 'timestamp')
    op.drop_column('results', 'start_group')
    op.drop_column('results', 'sta')
    op.drop_column('results', 'rider_class')
    op.drop_column('results', 'phase')
    op.drop_column('results', 'color')
    op.drop_column('persons', 'date_of_birth')
    op.drop_table('marks')
    # ### end Alembic commands ###
