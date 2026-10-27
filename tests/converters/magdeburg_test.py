"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path
from unittest.mock import Mock

import pytest
from requests_mock import Mocker
from syrupy.assertion import SnapshotAssertion

from parkapi_sources.converters.magdeburg import MagdeburgPullConverter
from parkapi_sources.util import RequestHelper
from tests.converters.helper import validate_realtime_parking_site_inputs, validate_static_parking_site_inputs


@pytest.fixture
def magdeburg_pull_converter(
    mocked_static_geojson_config_helper: Mock,
    request_helper: RequestHelper,
) -> MagdeburgPullConverter:
    return MagdeburgPullConverter(config_helper=mocked_static_geojson_config_helper, request_helper=request_helper)


class MagdeburgPullConverterTest:
    @staticmethod
    def test_get_static_parking_sites(
        magdeburg_pull_converter: MagdeburgPullConverter,
        snapshot: SnapshotAssertion,
    ):
        static_parking_site_inputs, import_parking_site_exceptions = magdeburg_pull_converter.get_static_parking_sites()

        assert len(static_parking_site_inputs) == 13
        assert len(import_parking_site_exceptions) == 0

        validate_static_parking_site_inputs(static_parking_site_inputs, snapshot)

    @staticmethod
    def test_get_realtime_parking_sites(
        magdeburg_pull_converter: MagdeburgPullConverter,
        requests_mock: Mocker,
        snapshot: SnapshotAssertion,
    ):
        html_path = Path(Path(__file__).parent, 'data', 'magdeburg.html')
        with html_path.open() as html_file:
            html_data = html_file.read()

        requests_mock.get('https://www.movi.de/parkinfo/uebersicht.shtml', text=html_data)

        realtime_parking_site_inputs, import_parking_site_exceptions = (
            magdeburg_pull_converter.get_realtime_parking_sites()
        )

        assert len(realtime_parking_site_inputs) == 10
        assert len(import_parking_site_exceptions) == 0

        validate_realtime_parking_site_inputs(realtime_parking_site_inputs, snapshot)
