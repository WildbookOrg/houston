"""empty message

Revision ID: 69accf38d040
Revises: ba12fedbea4e
Create Date: 2020-12-04 16:05:59.409002

"""

# revision identifiers, used by Alembic.
revision = '69accf38d040'
down_revision = 'ba12fedbea4e'

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils

import app
import app.extensions



def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('organization', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_guid', app.extensions.GUID(), nullable=True))
        batch_op.create_index(batch_op.f('ix_organization_user_guid'), ['user_guid'], unique=False)
        batch_op.create_foreign_key(batch_op.f('fk_organization_user_guid_user'), 'user', ['user_guid'], ['guid'], ondelete='CASCADE')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('organization', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_organization_user_guid_user'), type_='foreignkey')
        batch_op.drop_index(batch_op.f('ix_organization_user_guid'))
        batch_op.drop_column('user_guid')

    # ### end Alembic commands ###