"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path
from unittest.mock import Mock

import pytest
from requests_mock import Mocker
from syrupy.assertion import SnapshotAssertion

from parkapi_sources.converters.nuernberg import NuernbergPullConverter
from parkapi_sources.util import RequestHelper
from tests.converters.helper import validate_realtime_parking_site_inputs, validate_static_parking_site_inputs


@pytest.fixture
def nuernberg_pull_converter(
    mocked_static_geojson_config_helper: Mock,
    request_helper: RequestHelper,
) -> NuernbergPullConverter:
    return NuernbergPullConverter(config_helper=mocked_static_geojson_config_helper, request_helper=request_helper)


class NuernbergPullConverterTest:
    @staticmethod
    def test_get_static_parking_sites(
        nuernberg_pull_converter: NuernbergPullConverter,
        snapshot: SnapshotAssertion,
    ):
        static_parking_site_inputs, import_parking_site_exceptions = nuernberg_pull_converter.get_static_parking_sites()

        assert len(static_parking_site_inputs) == 19
        assert len(import_parking_site_exceptions) == 0

        validate_static_parking_site_inputs(static_parking_site_inputs, snapshot)

    @staticmethod
    def test_get_realtime_parking_sites(
        nuernberg_pull_converter: NuernbergPullConverter,
        requests_mock: Mocker,
        snapshot: SnapshotAssertion,
    ):
        html_path = Path(Path(__file__).parent, 'data', 'nuernberg.html')
        with html_path.open() as html_file:
            html_data = html_file.read()

        requests_mock.get(
            'https://tiefbauamt.nuernberg.de/site/parken/parkhausbelegung/parkhaus_belegung.html', text=html_data
        )

        realtime_parking_site_inputs, import_parking_site_exceptions = (
            nuernberg_pull_converter.get_realtime_parking_sites()
        )

        assert len(realtime_parking_site_inputs) == 19
        assert len(import_parking_site_exceptions) == 0

        validate_realtime_parking_site_inputs(realtime_parking_site_inputs, snapshot)
