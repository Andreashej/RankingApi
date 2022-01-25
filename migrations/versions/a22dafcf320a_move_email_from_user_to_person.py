"""move email from user to person

Revision ID: a22dafcf320a
Revises: 02244e7ab17d
Create Date: 2022-01-21 17:13:42.521572

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'a22dafcf320a'
down_revision = '02244e7ab17d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('competitions', sa.Column('contact_person_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'competitions', 'persons', ['contact_person_id'], ['id'])
    op.add_column('persons', sa.Column('email', sa.String(length=128), nullable=False))
    op.drop_column('users', 'email')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('email', mysql.VARCHAR(length=128), nullable=False))
    op.drop_column('persons', 'email')
    op.drop_constraint(None, 'competitions', type_='foreignkey')
    op.drop_column('competitions', 'contact_person_id')
    # ### end Alembic commands ###
