"""empty message

Revision ID: bef2e6475b02
Revises: a6b1cfd945f2
Create Date: 2021-05-17 16:43:43.679732

"""

# revision identifiers, used by Alembic.
revision = 'bef2e6475b02'
down_revision = 'a6b1cfd945f2'

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
    with op.batch_alter_table('asset_group', schema=None) as batch_op:
        batch_op.add_column(sa.Column('submitter_guid', app.extensions.GUID(), nullable=True))
        batch_op.create_index(batch_op.f('ix_asset_group_submitter_guid'), ['submitter_guid'], unique=False)
        batch_op.create_foreign_key(batch_op.f('fk_asset_group_submitter_guid_user'), 'user', ['submitter_guid'], ['guid'])

    with op.batch_alter_table('asset_group_sighting', schema=None) as batch_op:
        batch_op.add_column(sa.Column('meta', sa.JSON(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    """
    Downgrade Semantic Description:
        ENTER DESCRIPTION HERE
    """
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('asset_group_sighting', schema=None) as batch_op:
        batch_op.drop_column('meta')

    with op.batch_alter_table('asset_group', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_asset_group_submitter_guid_user'), type_='foreignkey')
        batch_op.drop_index(batch_op.f('ix_asset_group_submitter_guid'))
        batch_op.drop_column('submitter_guid')

    # ### end Alembic commands ###
