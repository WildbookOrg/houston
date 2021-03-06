# -*- coding: utf-8 -*-
import datetime
import pathlib
from unittest import mock
import uuid


def test_asset_group_sightings_jobs(flask_app, db, admin_user, test_root, request):
    from app.modules.asset_groups.models import AssetGroup, AssetGroupSighting

    transaction_id = str(uuid.uuid4())
    trans_dir = (
        pathlib.Path(flask_app.config['UPLOADS_DATABASE_PATH'])
        / f'trans-{transaction_id}'
    )
    trans_dir.mkdir(parents=True)
    with (trans_dir / 'zebra.jpg').open('wb') as f:
        with (test_root / 'zebra.jpg').open('rb') as g:
            f.write(g.read())
    asset_group = AssetGroup.create_from_tus(
        'test asset group description', admin_user, transaction_id
    )
    with db.session.begin():
        db.session.add(asset_group)
    request.addfinalizer(asset_group.delete)

    ags1 = AssetGroupSighting(
        config={'assetReferences': ['zebra.jpg']}, asset_group_guid=asset_group.guid
    )
    ags2 = AssetGroupSighting(
        config={'assetReferences': []}, asset_group_guid=asset_group.guid
    )
    with db.session.begin():
        db.session.add(ags1)
        db.session.add(ags2)
    request.addfinalizer(ags1.delete)
    request.addfinalizer(ags2.delete)

    now = datetime.datetime(2021, 7, 7, 17, 55, 34)
    job_id1 = uuid.UUID('53ea04e0-1e87-412d-aa17-0ff5e05db78d')
    job_id2 = uuid.UUID('fca55971-f014-4a8d-9e94-2c88b72d2d8c')

    uuids = [job_id2, job_id1]

    # Don't send anything to acm
    with mock.patch('app.modules.asset_groups.models.current_app'):
        with mock.patch('datetime.datetime') as mock_datetime:
            with mock.patch(
                'app.modules.asset_groups.models.uuid.uuid4', side_effect=uuids.pop
            ):
                mock_datetime.utcnow.return_value = now
                ags1.run_sage_detection('ags1-model')
                ags2.run_sage_detection('ags2-model')

    assert AssetGroupSighting.query.get(ags1.guid).jobs == {
        str(job_id1): {
            'model': 'ags1-model',
            'active': True,
            'start': now,
        },
    }
    assert AssetGroupSighting.query.get(ags2.guid).jobs == {
        str(job_id2): {
            'model': 'ags2-model',
            'active': True,
            'start': now,
        },
    }
