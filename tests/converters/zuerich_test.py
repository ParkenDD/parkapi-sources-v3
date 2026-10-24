"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path
from unittest.mock import Mock

import pytest
from requests_mock import Mocker
from syrupy.assertion import SnapshotAssertion

from parkapi_sources.converters.zuerich import ZuerichPullConverter
from parkapi_sources.util import RequestHelper
from tests.converters.helper import validate_realtime_parking_site_inputs, validate_static_parking_site_inputs


@pytest.fixture
def zuerich_pull_converter(
    mocked_static_geojson_config_helper: Mock,
    request_helper: RequestHelper,
) -> ZuerichPullConverter:
    return ZuerichPullConverter(config_helper=mocked_static_geojson_config_helper, request_helper=request_helper)


class ZuerichPullConverterTest:
    @staticmethod
    def test_get_static_parking_sites(
        zuerich_pull_converter: ZuerichPullConverter,
        snapshot: SnapshotAssertion,
    ):
        static_parking_site_inputs, import_parking_site_exceptions = zuerich_pull_converter.get_static_parking_sites()

        assert len(static_parking_site_inputs) == 36
        assert len(import_parking_site_exceptions) == 0

        validate_static_parking_site_inputs(static_parking_site_inputs, snapshot)

    @staticmethod
    def test_get_realtime_parking_sites(
        zuerich_pull_converter: ZuerichPullConverter,
        requests_mock: Mocker,
        snapshot: SnapshotAssertion,
    ):
        xml_path = Path(Path(__file__).parent, 'data', 'zuerich.xml')
        with xml_path.open() as xml_file:
            xml_data = xml_file.read()

        requests_mock.get('https://www.pls-zh.ch/plsFeed/rss', text=xml_data)

        realtime_parking_site_inputs, import_parking_site_exceptions = (
            zuerich_pull_converter.get_realtime_parking_sites()
        )

        assert len(realtime_parking_site_inputs) == 35
        assert len(import_parking_site_exceptions) == 0

        validate_realtime_parking_site_inputs(realtime_parking_site_inputs, snapshot)
