"""empty message

Revision ID: 060344b8b804
Revises: 1d3098a15e4f
Create Date: 2021-01-15 23:58:21.353918

"""

# revision identifiers, used by Alembic.
revision = '060344b8b804'
down_revision = '1d3098a15e4f'

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils

import app
import app.extensions



def upgrade():
    """
    Upgrade Semantic Description:
        ENTER DESCRIPTION HERE
    """
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('houston_config',
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=False),
    sa.Column('viewed', sa.DateTime(), nullable=False),
    sa.Column('guid', app.extensions.GUID(), nullable=False),
    sa.Column('key', sa.String(), nullable=False),
    sa.Column('value', sa.JSON(), nullable=False),
    sa.PrimaryKeyConstraint('guid', name=op.f('pk_houston_config')),
    sa.UniqueConstraint('key', name=op.f('uq_houston_config_key'))
    )
    with op.batch_alter_table('project', schema=None) as batch_op:
        batch_op.add_column(sa.Column('viewed', sa.DateTime(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    """
    Downgrade Semantic Description:
        ENTER DESCRIPTION HERE
    """
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('project', schema=None) as batch_op:
        batch_op.drop_column('viewed')

    op.drop_table('houston_config')
    # ### end Alembic commands ###