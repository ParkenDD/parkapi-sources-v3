"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path
from unittest.mock import Mock

import pytest
from requests_mock import Mocker
from syrupy.assertion import SnapshotAssertion

from parkapi_sources.converters.bfrk_bw import BfrkBwBikePullConverter, BfrkBwCarPullConverter
from parkapi_sources.util import RequestHelper
from tests.converters.helper import validate_static_parking_site_inputs, validate_static_parking_spot_inputs


@pytest.fixture
def mocked_bfrk_bw_config_helper(mocked_config_helper: Mock):
    config = {}
    mocked_config_helper.get.side_effect = lambda key, default=None: config.get(key, default)
    return mocked_config_helper


@pytest.fixture
def mocked_bfrk_bw_config_helper_no_filter(mocked_config_helper: Mock):
    config = {
        'PARK_API_BFRK_BW_CAR_FILTER_UNCONFIRMED': False,
        'PARK_API_BFRK_BW_BIKE_FILTER_UNCONFIRMED': False,
    }
    mocked_config_helper.get.side_effect = lambda key, default=None: config.get(key, default)
    return mocked_config_helper


@pytest.fixture
def mocked_bfrk_bw_config_helper_no_filter_private(mocked_config_helper: Mock):
    config = {
        'PARK_API_BFRK_BW_CAR_FILTER_UNCONFIRMED': False,
        'PARK_API_BFRK_BW_CAR_FILTER_PRIVATE': False,
    }
    mocked_config_helper.get.side_effect = lambda key, default=None: config.get(key, default)
    return mocked_config_helper


@pytest.fixture
def mocked_bfrk_bw_config_helper_no_ignore_missing_capacities(mocked_config_helper: Mock):
    config = {
        'PARK_API_BFRK_BW_BIKE_IGNORE_MISSING_CAPACITIES': False,
    }
    mocked_config_helper.get.side_effect = lambda key, default=None: config.get(key, default)
    return mocked_config_helper


@pytest.fixture
def bfrk_car_pull_converter(
    mocked_bfrk_bw_config_helper: Mock,
    request_helper: RequestHelper,
) -> BfrkBwCarPullConverter:
    return BfrkBwCarPullConverter(config_helper=mocked_bfrk_bw_config_helper, request_helper=request_helper)


@pytest.fixture
def bfrk_car_pull_converter_unconfirmed(
    mocked_bfrk_bw_config_helper_no_filter: Mock,
    request_helper: RequestHelper,
) -> BfrkBwCarPullConverter:
    return BfrkBwCarPullConverter(config_helper=mocked_bfrk_bw_config_helper_no_filter, request_helper=request_helper)


@pytest.fixture
def bfrk_car_pull_converter_no_filter_private(
    mocked_bfrk_bw_config_helper_no_filter_private: Mock,
    request_helper: RequestHelper,
) -> BfrkBwCarPullConverter:
    return BfrkBwCarPullConverter(
        config_helper=mocked_bfrk_bw_config_helper_no_filter_private,
        request_helper=request_helper,
    )


class BfrkCarPullConverterTest:
    @staticmethod
    def test_get_static_parking_sites(
        bfrk_car_pull_converter: BfrkBwCarPullConverter,
        requests_mock: Mocker,
        snapshot: SnapshotAssertion,
    ):
        json_path = Path(Path(__file__).parent, 'data', 'bfrk_bw_car.json')
        with json_path.open() as json_file:
            json_data = json_file.read()

        requests_mock.get(
            'https://bfrk-kat-api.efa-bw.de/bfrk_api/parkplaetze',
            text=json_data,
        )

        static_parking_site_inputs, import_parking_site_exceptions = bfrk_car_pull_converter.get_static_parking_sites()

        assert len(static_parking_site_inputs) == 1482
        assert len(import_parking_site_exceptions) == 9

        validate_static_parking_site_inputs(static_parking_site_inputs, snapshot)

    @staticmethod
    def test_get_static_parking_sites_unconfirmed(
        bfrk_car_pull_converter_unconfirmed: BfrkBwCarPullConverter,
        requests_mock: Mocker,
        snapshot: SnapshotAssertion,
    ):
        json_path = Path(Path(__file__).parent, 'data', 'bfrk_bw_car.json')
        with json_path.open() as json_file:
            json_data = json_file.read()

        requests_mock.get(
            'https://bfrk-kat-api.efa-bw.de/bfrk_api/parkplaetze',
            text=json_data,
        )

        static_parking_site_inputs, import_parking_site_exceptions = (
            bfrk_car_pull_converter_unconfirmed.get_static_parking_sites()
        )

        assert len(static_parking_site_inputs) == 2127
        assert len(import_parking_site_exceptions) == 9

        validate_static_parking_site_inputs(static_parking_site_inputs, snapshot)

    @staticmethod
    def test_get_static_parking_spots(
        bfrk_car_pull_converter: BfrkBwCarPullConverter,
        requests_mock: Mocker,
        snapshot: SnapshotAssertion,
    ):
        json_path = Path(Path(__file__).parent, 'data', 'bfrk_bw_car.json')
        with json_path.open() as json_file:
            json_data = json_file.read()

        requests_mock.get(
            'https://bfrk-kat-api.efa-bw.de/bfrk_api/parkplaetze',
            text=json_data,
        )

        static_parking_spot_inputs, import_parking_site_exceptions = bfrk_car_pull_converter.get_static_parking_spots()
        assert len(static_parking_spot_inputs) == 1395
        assert len(import_parking_site_exceptions) == 9

        validate_static_parking_spot_inputs(static_parking_spot_inputs, snapshot)

    @staticmethod
    def test_get_static_parking_spots_unconfirmed(
        bfrk_car_pull_converter_unconfirmed: BfrkBwCarPullConverter,
        requests_mock: Mocker,
        snapshot: SnapshotAssertion,
    ):
        json_path = Path(Path(__file__).parent, 'data', 'bfrk_bw_car.json')
        with json_path.open() as json_file:
            json_data = json_file.read()

        requests_mock.get(
            'https://bfrk-kat-api.efa-bw.de/bfrk_api/parkplaetze',
            text=json_data,
        )

        static_parking_spot_inputs, import_parking_site_exceptions = (
            bfrk_car_pull_converter_unconfirmed.get_static_parking_spots()
        )
        assert len(static_parking_spot_inputs) == 1395
        assert len(import_parking_site_exceptions) == 9

        validate_static_parking_spot_inputs(static_parking_spot_inputs, snapshot)

    @staticmethod
    def test_get_static_parking_sites_no_filter_private(
        bfrk_car_pull_converter_no_filter_private: BfrkBwCarPullConverter,
        requests_mock: Mocker,
    ):
        json_path = Path(Path(__file__).parent, 'data', 'bfrk_bw_car.json')
        with json_path.open() as json_file:
            json_data = json_file.read()

        requests_mock.get(
            'https://bfrk-kat-api.efa-bw.de/bfrk_api/parkplaetze',
            text=json_data,
        )

        static_parking_site_inputs, import_parking_site_exceptions = (
            bfrk_car_pull_converter_no_filter_private.get_static_parking_sites()
        )

        assert len(static_parking_site_inputs) == 2127
        assert len(import_parking_site_exceptions) == 9


@pytest.fixture
def bfrk_bike_pull_converter(
    mocked_bfrk_bw_config_helper: Mock,
    request_helper: RequestHelper,
) -> BfrkBwBikePullConverter:
    return BfrkBwBikePullConverter(config_helper=mocked_bfrk_bw_config_helper, request_helper=request_helper)


@pytest.fixture
def bfrk_bike_pull_converter_unconfirmed(
    mocked_bfrk_bw_config_helper_no_filter: Mock,
    request_helper: RequestHelper,
) -> BfrkBwBikePullConverter:
    return BfrkBwBikePullConverter(config_helper=mocked_bfrk_bw_config_helper_no_filter, request_helper=request_helper)


@pytest.fixture
def bfrk_bike_pull_converter_no_ignore_missing_capacities(
    mocked_bfrk_bw_config_helper_no_ignore_missing_capacities: Mock,
    request_helper: RequestHelper,
) -> BfrkBwBikePullConverter:
    return BfrkBwBikePullConverter(
        config_helper=mocked_bfrk_bw_config_helper_no_ignore_missing_capacities,
        request_helper=request_helper,
    )


class BfrkBikePullConverterTest:
    @staticmethod
    def test_get_static_parking_sites(
        bfrk_bike_pull_converter: BfrkBwBikePullConverter,
        requests_mock: Mocker,
        snapshot: SnapshotAssertion,
    ):
        json_path = Path(Path(__file__).parent, 'data', 'bfrk_bw_bike.json')
        with json_path.open() as json_file:
            json_data = json_file.read()

        requests_mock.get(
            'https://bfrk-kat-api.efa-bw.de/bfrk_api/fahrradanlagen',
            text=json_data,
        )

        static_parking_site_inputs, import_parking_site_exceptions = bfrk_bike_pull_converter.get_static_parking_sites()

        assert len(static_parking_site_inputs) == 1994
        assert len(import_parking_site_exceptions) == 0

        validate_static_parking_site_inputs(static_parking_site_inputs, snapshot)

    @staticmethod
    def test_get_static_parking_sites_unconfirmed(
        bfrk_bike_pull_converter_unconfirmed: BfrkBwBikePullConverter,
        requests_mock: Mocker,
        snapshot: SnapshotAssertion,
    ):
        json_path = Path(Path(__file__).parent, 'data', 'bfrk_bw_bike.json')
        with json_path.open() as json_file:
            json_data = json_file.read()

        requests_mock.get(
            'https://bfrk-kat-api.efa-bw.de/bfrk_api/fahrradanlagen',
            text=json_data,
        )

        static_parking_site_inputs, import_parking_site_exceptions = (
            bfrk_bike_pull_converter_unconfirmed.get_static_parking_sites()
        )

        assert len(static_parking_site_inputs) == 2877
        assert len(import_parking_site_exceptions) == 0

        validate_static_parking_site_inputs(static_parking_site_inputs, snapshot)

    @staticmethod
    def test_get_static_parking_sites_no_ignore_missing_capacities(
        bfrk_bike_pull_converter_no_ignore_missing_capacities: BfrkBwBikePullConverter,
        requests_mock: Mocker,
    ):
        json_path = Path(Path(__file__).parent, 'data', 'bfrk_bw_bike.json')
        with json_path.open() as json_file:
            json_data = json_file.read()

        requests_mock.get(
            'https://bfrk-kat-api.efa-bw.de/bfrk_api/fahrradanlagen',
            text=json_data,
        )

        static_parking_site_inputs, import_parking_site_exceptions = (
            bfrk_bike_pull_converter_no_ignore_missing_capacities.get_static_parking_sites()
        )

        assert len(static_parking_site_inputs) == 1994
        assert len(import_parking_site_exceptions) == 153
