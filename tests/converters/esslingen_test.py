"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import json
from unittest.mock import Mock

import pytest

from parkapi_sources.converters import EsslingenPushConverter
from parkapi_sources.util import RequestHelper
from tests.converters.helper import get_data_path, validate_static_parking_site_inputs


@pytest.fixture
def esslingen_push_converter(mocked_config_helper: Mock, request_helper: RequestHelper) -> EsslingenPushConverter:
    return EsslingenPushConverter(config_helper=mocked_config_helper, request_helper=request_helper)


class EsslingenPushConverterTest:
    @staticmethod
    def test_get_static_parking_sites(esslingen_push_converter: EsslingenPushConverter):
        with get_data_path('esslingen.geojson').open() as esslingen_file:
            esslingen_data = json.loads(esslingen_file.read())

        static_parking_site_inputs, import_parking_site_exceptions = esslingen_push_converter.handle_json(
            esslingen_data,
        )

        assert len(static_parking_site_inputs) == 211
        assert len(import_parking_site_exceptions) == 6

        validate_static_parking_site_inputs(static_parking_site_inputs)
