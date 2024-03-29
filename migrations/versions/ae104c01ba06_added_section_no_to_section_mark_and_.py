"""added section_no to section mark and renamed parent column

Revision ID: ae104c01ba06
Revises: d6d97ed173b2
Create Date: 2022-02-25 20:48:10.472134

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'ae104c01ba06'
down_revision = 'd6d97ed173b2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('marks', sa.Column('judge_mark_id', sa.Integer(), nullable=True))
    op.add_column('marks', sa.Column('section_no', sa.Integer(), nullable=True))
    op.drop_constraint('marks_ibfk_2', 'marks', type_='foreignkey')
    op.create_foreign_key(None, 'marks', 'marks', ['judge_mark_id'], ['id'])
    op.drop_column('marks', 'section_mark_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('marks', sa.Column('section_mark_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'marks', type_='foreignkey')
    op.create_foreign_key('marks_ibfk_2', 'marks', 'marks', ['section_mark_id'], ['id'])
    op.drop_column('marks', 'section_no')
    op.drop_column('marks', 'judge_mark_id')
    # ### end Alembic commands ###
