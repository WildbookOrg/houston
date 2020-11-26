# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring

from app.modules.assets.models import Asset
from app.modules.submissions.models import Submission
from tests.utils import CloneSubmission


def test_find_asset(
    flask_app_client, regular_user, db, test_clone_submission_uuid, test_asset_uuid
):
    # Clone the known submission so that the asset data is in the database
    response = CloneSubmission(flask_app_client, regular_user, test_clone_submission_uuid)

    # But now remove the files so that Houston knows about the asset but does not have the files
    response.remove_files()

    db_asset = Asset.query.get(test_asset_uuid)
    db_submission = Submission.query.get(test_clone_submission_uuid)
    assert(db_asset == db_submission.assets[1])
    # print("Found Asset {} {}".format(db_asset, db_submission))
    # breakpoint()
