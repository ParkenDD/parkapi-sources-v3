"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path
from unittest.mock import Mock

import pytest
from requests_mock import Mocker
from syrupy.assertion import SnapshotAssertion

from parkapi_sources.converters.dresden import DresdenPullConverter
from parkapi_sources.util import RequestHelper
from tests.converters.helper import validate_realtime_parking_site_inputs, validate_static_parking_site_inputs


@pytest.fixture
def dresden_pull_converter(
    mocked_static_geojson_config_helper: Mock,
    request_helper: RequestHelper,
) -> DresdenPullConverter:
    return DresdenPullConverter(config_helper=mocked_static_geojson_config_helper, request_helper=request_helper)


class DresdenPullConverterTest:
    @staticmethod
    def test_get_static_parking_sites(
        dresden_pull_converter: DresdenPullConverter,
        snapshot: SnapshotAssertion,
    ):
        static_parking_site_inputs, import_parking_site_exceptions = dresden_pull_converter.get_static_parking_sites()

        assert len(static_parking_site_inputs) == 54
        assert len(import_parking_site_exceptions) == 0

        validate_static_parking_site_inputs(static_parking_site_inputs, snapshot)

    @staticmethod
    def test_get_realtime_parking_sites(
        dresden_pull_converter: DresdenPullConverter,
        requests_mock: Mocker,
        snapshot: SnapshotAssertion,
    ):
        html_path = Path(Path(__file__).parent, 'data', 'dresden.html')
        with html_path.open() as html_file:
            html_data = html_file.read()

        requests_mock.get('https://www.dresden.de/apps_ext/ParkplatzApp/', text=html_data)

        realtime_parking_site_inputs, import_parking_site_exceptions = (
            dresden_pull_converter.get_realtime_parking_sites()
        )

        assert len(realtime_parking_site_inputs) == 40
        assert len(import_parking_site_exceptions) == 0

        validate_realtime_parking_site_inputs(realtime_parking_site_inputs, snapshot)
