"""Initial migration

Revision ID: b447f2b4e8f3
Revises: 
Create Date: 2022-05-16 11:50:19.196819

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b447f2b4e8f3'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('devices',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('dev_id', sa.String(length=200), nullable=False),
    sa.Column('dev_type', sa.String(length=120), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('endpoints',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('device_id', sa.Integer(), nullable=True),
    sa.Column('comment', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['device_id'], ['devices.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('endpoints')
    op.drop_table('devices')
    # ### end Alembic commands ###
