"""empty message

Revision ID: 9e71ecc2708a
Revises: 9b2a1efceeec
Create Date: 2021-05-27 20:19:49.829026

"""

# revision identifiers, used by Alembic.
revision = '9e71ecc2708a'
down_revision = '9b2a1efceeec'

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils

import app
import app.extensions

from sqlalchemy.dialects import postgresql

def upgrade():
    """
    Upgrade Semantic Description:
        ENTER DESCRIPTION HERE
    """
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('annotation', schema=None) as batch_op:
        batch_op.alter_column('encounter_guid',
               existing_type=postgresql.UUID(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    """
    Downgrade Semantic Description:
        ENTER DESCRIPTION HERE
    """
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('annotation', schema=None) as batch_op:
        batch_op.alter_column('encounter_guid',
               existing_type=postgresql.UUID(),
               nullable=False)

    # ### end Alembic commands ###
