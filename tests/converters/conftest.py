"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import re
from unittest.mock import Mock

import pytest
from requests_mock import Mocker
from syrupy.assertion import SnapshotAssertion
from syrupy.extensions.json import JSONSnapshotExtension

from tests.converters.helper import static_geojson_callback

STATIC_GEOJSON_BASE_URL = 'https://raw.githubusercontent.com/ParkenDD/parkapi-static-data/main/sources'


@pytest.fixture
def mocked_static_geojson_config_helper(mocked_config_helper: Mock, requests_mock: Mocker) -> Mock:
    # Serve static GeoJSON from local test data, so snapshots don't depend on upstream changes
    requests_mock.get(re.compile(rf'{re.escape(STATIC_GEOJSON_BASE_URL)}/.+\.geojson'), json=static_geojson_callback)

    config = {'STATIC_GEOJSON_BASE_URL': STATIC_GEOJSON_BASE_URL}
    mocked_config_helper.get.side_effect = lambda key, default=None: config.get(key, default)
    return mocked_config_helper


@pytest.fixture
def snapshot(snapshot: SnapshotAssertion) -> SnapshotAssertion:
    # Store converter results as JSON, which is much faster to compare than amber for large datasets
    return snapshot.use_extension(JSONSnapshotExtension)
