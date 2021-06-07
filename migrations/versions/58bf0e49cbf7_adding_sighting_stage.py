"""adding sighting stage

Revision ID: 58bf0e49cbf7
Revises: adb5d1a314bc
Create Date: 2021-06-07 19:52:25.795223

"""

# revision identifiers, used by Alembic.
revision = '58bf0e49cbf7'
down_revision = 'adb5d1a314bc'

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
    with op.batch_alter_table('sighting', schema=None) as batch_op:
        batch_op.add_column(sa.Column('stage', sa.Enum('identification', 'un_reviewed', 'processed', 'failed', name='sightingstage'), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    """
    Downgrade Semantic Description:
        ENTER DESCRIPTION HERE
    """
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('sighting', schema=None) as batch_op:
        batch_op.drop_column('stage')
    sa.Enum(name='sightingstage').drop(op.get_bind(), checkfirst=False)
    # ### end Alembic commands ###
