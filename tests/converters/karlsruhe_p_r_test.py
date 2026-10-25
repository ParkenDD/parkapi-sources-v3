"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from unittest.mock import Mock

import pytest
from requests_mock import Mocker
from syrupy.assertion import SnapshotAssertion

from parkapi_sources.converters import KarlsruheParkAndRidePullConverter
from parkapi_sources.util import RequestHelper
from tests.converters.helper import (
    get_data_path,
    validate_realtime_parking_site_inputs,
    validate_static_parking_site_inputs,
)


@pytest.fixture
def karlsruhe_p_r_config_helper(mocked_config_helper: Mock):
    # Use the defaults of the converter, e.g. to ignore parking sites without capacity
    mocked_config_helper.get.side_effect = lambda key, default=None: default
    return mocked_config_helper


@pytest.fixture
def karlsruhe_p_r_pull_converter(
    karlsruhe_p_r_config_helper: Mock,
    request_helper: RequestHelper,
) -> KarlsruheParkAndRidePullConverter:
    return KarlsruheParkAndRidePullConverter(config_helper=karlsruhe_p_r_config_helper, request_helper=request_helper)


class KarlsruheParkAndRidePullConverterTest:
    @staticmethod
    def test_get_static_parking_sites(
        karlsruhe_p_r_pull_converter: KarlsruheParkAndRidePullConverter,
        requests_mock: Mocker,
        snapshot: SnapshotAssertion,
    ):
        requests_mock.get(
            'https://mobil.trk.de/geoserver/TBA/ows', text=get_data_path('karlsruhe_p_r.json').read_text()
        )

        static_parking_site_inputs, import_parking_site_exceptions = (
            karlsruhe_p_r_pull_converter.get_static_parking_sites()
        )

        assert len(static_parking_site_inputs) == 167
        assert len(import_parking_site_exceptions) == 0

        validate_static_parking_site_inputs(static_parking_site_inputs, snapshot)

    @staticmethod
    def test_get_realtime_parking_sites(
        karlsruhe_p_r_pull_converter: KarlsruheParkAndRidePullConverter,
        requests_mock: Mocker,
        snapshot: SnapshotAssertion,
    ):
        requests_mock.get(
            'https://mobil.trk.de/geoserver/TBA/ows', text=get_data_path('karlsruhe_p_r.json').read_text()
        )

        realtime_parking_site_inputs, import_parking_site_exceptions = (
            karlsruhe_p_r_pull_converter.get_realtime_parking_sites()
        )

        assert len(realtime_parking_site_inputs) == 5
        assert len(import_parking_site_exceptions) == 0

        validate_realtime_parking_site_inputs(realtime_parking_site_inputs, snapshot)
