"""add test_id to screengroups

Revision ID: 37268177acac
Revises: bd8d86ce0fdb
Create Date: 2022-02-09 23:40:42.798700

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '37268177acac'
down_revision = 'bd8d86ce0fdb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('screengroups', sa.Column('test_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'screengroups', 'tests', ['test_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'screengroups', type_='foreignkey')
    op.drop_column('screengroups', 'test_id')
    # ### end Alembic commands ###