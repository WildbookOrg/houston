"""empty message

Revision ID: fc3498d68351
Revises: fca2aa76992c
Create Date: 2020-12-18 11:35:56.386830

"""

# revision identifiers, used by Alembic.
revision = 'fc3498d68351'
down_revision = 'fca2aa76992c'

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils

import app
import app.extensions



def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('encounter', schema=None) as batch_op:
        batch_op.add_column(sa.Column('owner_guid', app.extensions.GUID(), nullable=True))
        batch_op.create_index(batch_op.f('ix_encounter_owner_guid'), ['owner_guid'], unique=False)
        batch_op.drop_constraint('fk_encounter_sighting_id_sighting', type_='foreignkey')
        batch_op.create_foreign_key(batch_op.f('fk_encounter_owner_guid_user'), 'user', ['owner_guid'], ['guid'])
        batch_op.drop_column('sighting_id')
        batch_op.drop_column('owner')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('encounter', schema=None) as batch_op:
        batch_op.add_column(sa.Column('owner', sa.CHAR(length=32), nullable=True))
        batch_op.add_column(sa.Column('sighting_id', sa.INTEGER(), nullable=True))
        batch_op.drop_constraint(batch_op.f('fk_encounter_owner_guid_user'), type_='foreignkey')
        batch_op.create_foreign_key('fk_encounter_sighting_id_sighting', 'sighting', ['sighting_id'], ['guid'])
        batch_op.drop_index(batch_op.f('ix_encounter_owner_guid'))
        batch_op.drop_column('owner_guid')

    # ### end Alembic commands ###