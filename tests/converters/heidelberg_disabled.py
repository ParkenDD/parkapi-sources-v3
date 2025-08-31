"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path
from unittest.mock import Mock

import pytest
from requests_mock import Mocker

from parkapi_sources.converters import HeidelbergDisabledPullConverter
from parkapi_sources.util import RequestHelper
from tests.converters.helper import validate_static_parking_spot_inputs


@pytest.fixture
def heidelberg_disabled_pull_converter(
    mocked_config_helper: Mock,
    request_helper: RequestHelper,
) -> HeidelbergDisabledPullConverter:
    return HeidelbergDisabledPullConverter(
        config_helper=mocked_config_helper,
        request_helper=request_helper,
    )


@pytest.fixture
def requests_mock_heidelberg_disabled(requests_mock: Mocker) -> Mocker:
    json_path = Path(Path(__file__).parent, 'data', 'heidelberg_disabled.geojson')
    with json_path.open() as json_file:
        json_data = json_file.read()

    requests_mock.get(
        'https://ckan.datenplattform.heidelberg.de/de/dataset/708df8e2-d452-483e-9e57-f04027d52a17/resource'
        '/6dc64728-65ba-47ed-bbe2-9e59b5dbaa0c/download/features_new.geojson',
        text=json_data,
    )

    return requests_mock


class HeidelbergDisabledConverterTest:
    @staticmethod
    def test_get_static_parking_spots(
        heidelberg_disabled_pull_converter: HeidelbergDisabledPullConverter,
        requests_mock_heidelberg_disabled: Mocker,
    ):
        static_parking_spot_inputs, import_parking_spot_exceptions = (
            heidelberg_disabled_pull_converter.get_static_parking_spots()
        )

        assert len(static_parking_spot_inputs) == 192
        assert len(import_parking_spot_exceptions) == 0

        validate_static_parking_spot_inputs(static_parking_spot_inputs)
