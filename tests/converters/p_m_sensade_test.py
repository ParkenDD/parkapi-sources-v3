"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path
from unittest.mock import Mock

import pytest
from requests_mock import Mocker

from parkapi_sources.converters import PMSensadePullConverter
from parkapi_sources.util import RequestHelper
from tests.converters.helper import (
    validate_realtime_parking_site_inputs,
    validate_static_parking_site_inputs,
    validate_static_parking_spot_inputs,
)


@pytest.fixture
def p_m_sensade_config_helper(mocked_config_helper: Mock):
    config = {
        'PARK_API_P_M_SENSADE_EMAIL': 'mobidatabw@nvbw.de',
        'PARK_API_P_M_SENSADE_PASSWORD': 'password',
    }
    mocked_config_helper.get.side_effect = lambda key, default=None: config.get(key, default)
    return mocked_config_helper


@pytest.fixture
def p_m_sensade_pull_converter(
    p_m_sensade_config_helper: Mock,
    request_helper: RequestHelper,
) -> PMSensadePullConverter:
    return PMSensadePullConverter(config_helper=p_m_sensade_config_helper, request_helper=request_helper)


class UlmSensorsPullConverterTest:
    @staticmethod
    def _test_get_raw_parking_sites(
        p_m_sensade_pull_converter: PMSensadePullConverter,
        requests_mock: Mocker,
    ):
        json_path = Path(Path(__file__).parent, 'data', 'p-m-sensade', 'parking-lots.json')
        with json_path.open() as json_file:
            json_data = json_file.read()

        requests_mock.post(
            'https://api.sensade.com/auth/login',
            text='token',
        )
        requests_mock.get('https://api.sensade.com/parkinglot/parkinglot', text=json_data)

        raw_parking_site_inputs, import_parking_site_exceptions = p_m_sensade_pull_converter._get_sensade_parking_lots()

        assert len(raw_parking_site_inputs) == 7
        assert len(import_parking_site_exceptions) == 0

        return raw_parking_site_inputs, import_parking_site_exceptions

    @staticmethod
    def test_get_static_parking_sites(
        p_m_sensade_pull_converter: PMSensadePullConverter,
        requests_mock: Mocker,
    ):
        raw_parking_sites = UlmSensorsPullConverterTest._test_get_raw_parking_sites(
            p_m_sensade_pull_converter, requests_mock
        )

        for raw_parking_site in raw_parking_sites[0]:
            requests_mock.post(
                'https://api.sensade.com/auth/login',
                text='token',
            )

            json_path = Path(Path(__file__).parent, 'data', 'p-m-sensade', f'parking-lot-{raw_parking_site.id}.json')
            with json_path.open() as json_file:
                json_data = json_file.read()

            requests_mock.get(
                f'https://api.sensade.com/parkinglot/parkinglot/{raw_parking_site.id}',
                text=json_data,
            )

        static_parking_site_inputs, import_parking_site_exceptions = (
            p_m_sensade_pull_converter.get_static_parking_sites()
        )

        assert len(static_parking_site_inputs) == 7
        assert len(import_parking_site_exceptions) == 0

        validate_static_parking_site_inputs(static_parking_site_inputs)

    @staticmethod
    def test_get_realtime_parking_sites(
        p_m_sensade_pull_converter: PMSensadePullConverter,
        requests_mock: Mocker,
    ):
        raw_parking_sites = UlmSensorsPullConverterTest._test_get_raw_parking_sites(
            p_m_sensade_pull_converter, requests_mock
        )

        for raw_parking_site in raw_parking_sites[0]:
            requests_mock.post(
                'https://api.sensade.com/auth/login',
                text='token',
            )

            json_path = Path(
                Path(__file__).parent, 'data', 'p-m-sensade', f'parking-lot-status-{raw_parking_site.id}.json'
            )
            with json_path.open() as json_file:
                json_data = json_file.read()

            requests_mock.get(
                f'https://api.sensade.com/parkinglot/parkinglot/getcurrentparkinglotstatus/{raw_parking_site.id}',
                text=json_data,
            )

        realtime_parking_site_inputs, import_parking_site_exceptions = (
            p_m_sensade_pull_converter.get_realtime_parking_sites()
        )

        assert len(realtime_parking_site_inputs) == 7
        assert len(import_parking_site_exceptions) == 0

        validate_realtime_parking_site_inputs(realtime_parking_site_inputs)

    @staticmethod
    def test_get_static_parking_spots(
        p_m_sensade_pull_converter: PMSensadePullConverter,
        requests_mock: Mocker,
    ):
        raw_parking_sites = UlmSensorsPullConverterTest._test_get_raw_parking_sites(
            p_m_sensade_pull_converter, requests_mock
        )

        for raw_parking_site in raw_parking_sites[0]:
            requests_mock.post(
                'https://api.sensade.com/auth/login',
                text='token',
            )

            json_path = Path(Path(__file__).parent, 'data', 'p-m-sensade', f'parking-lot-{raw_parking_site.id}.json')
            with json_path.open() as json_file:
                json_data = json_file.read()

            requests_mock.get(
                f'https://api.sensade.com/parkinglot/parkinglot/{raw_parking_site.id}',
                text=json_data,
            )

        static_parking_spot_inputs, import_parking_spot_exceptions = (
            p_m_sensade_pull_converter.get_static_parking_spots()
        )

        assert len(static_parking_spot_inputs) == 580
        assert len(import_parking_spot_exceptions) == 0

        validate_static_parking_spot_inputs(static_parking_spot_inputs)
