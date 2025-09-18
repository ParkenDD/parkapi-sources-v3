"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path
from unittest.mock import Mock

import pytest
from requests_mock import Mocker

from parkapi_sources.converters import (
    FreiburgParkAndRideRealtimePullConverter,
    FreiburgParkAndRideStaticPullConverter,
)
from parkapi_sources.util import RequestHelper
from tests.converters.helper import validate_realtime_parking_site_inputs, validate_static_parking_site_inputs


@pytest.fixture
def freiburg_park_and_ride_static_pull_converter(
    mocked_static_geojson_config_helper: Mock,
    request_helper: RequestHelper,
) -> FreiburgParkAndRideStaticPullConverter:
    return FreiburgParkAndRideStaticPullConverter(
        config_helper=mocked_static_geojson_config_helper, request_helper=request_helper
    )


@pytest.fixture
def freiburg_park_and_ride_realtime_pull_converter(
    mocked_static_geojson_config_helper: Mock,
    request_helper: RequestHelper,
) -> FreiburgParkAndRideRealtimePullConverter:
    return FreiburgParkAndRideRealtimePullConverter(
        config_helper=mocked_static_geojson_config_helper, request_helper=request_helper
    )


def freiburg_request_mocked_json(requests_mock: Mocker, filename: str):
    # We need to get GeoJSON data
    requests_mock.real_http = True

    json_path = Path(Path(__file__).parent, 'data', filename)
    with json_path.open() as json_file:
        json_data = json_file.read()

    if 'sensors' in filename:
        requests_mock.get(
            'https://geoportal.freiburg.de/wfs/gdm_pls/gdm_pls?SERVICE=WFS&REQUEST=GetFeature&SRSNAME=EPSG:4326&SERVICE=WFS&VERSION=2.0.0&TYPENAMES=parkandride_aktuell&OUTPUTFORMAT=geojson&crs=4326',
            text=json_data,
        )
    else:
        requests_mock.get(
            'https://geoportal.freiburg.de/wfs/gdm_pls/gdm_pls?SERVICE=WFS&REQUEST=GetFeature&SRSNAME=EPSG:4326&SERVICE=WFS&VERSION=2.0.0&TYPENAMES=parkandride&OUTPUTFORMAT=geojson&crs=4326',
            text=json_data,
        )


class FreiburgParkAndRideStaticPullConverterTest:
    @staticmethod
    def test_get_static_parking_sites(
        freiburg_park_and_ride_static_pull_converter: FreiburgParkAndRideStaticPullConverter,
        requests_mock: Mocker,
    ):
        freiburg_request_mocked_json(requests_mock, 'freiburg_p_r_static.json')

        static_parking_site_inputs, import_parking_site_exceptions = (
            freiburg_park_and_ride_static_pull_converter.get_static_parking_sites()
        )

        assert len(static_parking_site_inputs) == 15
        assert len(import_parking_site_exceptions) == 0

        validate_static_parking_site_inputs(static_parking_site_inputs)


class FreiburgParkAndRideRealtimePullConverterTest:
    @staticmethod
    def test_get_static_parking_sites(
        freiburg_park_and_ride_realtime_pull_converter: FreiburgParkAndRideRealtimePullConverter,
        requests_mock: Mocker,
    ):
        freiburg_request_mocked_json(requests_mock, 'freiburg_p_r_sensors.json')

        static_parking_site_inputs, import_parking_site_exceptions = (
            freiburg_park_and_ride_realtime_pull_converter.get_static_parking_sites()
        )

        assert len(static_parking_site_inputs) == 5
        assert len(import_parking_site_exceptions) == 0

        validate_static_parking_site_inputs(static_parking_site_inputs)

    @staticmethod
    def test_get_realtime_parking_sites(
        freiburg_park_and_ride_realtime_pull_converter: FreiburgParkAndRideRealtimePullConverter,
        requests_mock: Mocker,
    ):
        freiburg_request_mocked_json(requests_mock, 'freiburg_p_r_sensors.json')

        realtime_parking_site_inputs, import_parking_site_exceptions = (
            freiburg_park_and_ride_realtime_pull_converter.get_realtime_parking_sites()
        )

        assert len(realtime_parking_site_inputs) == 5
        assert len(import_parking_site_exceptions) == 0

        validate_realtime_parking_site_inputs(realtime_parking_site_inputs)
