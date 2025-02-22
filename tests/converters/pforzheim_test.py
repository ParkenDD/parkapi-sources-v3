"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import json
from unittest.mock import Mock

import pytest

from parkapi_sources.converters import PforzheimPushConverter
from parkapi_sources.util import RequestHelper
from tests.converters.helper import get_data_path, validate_static_parking_site_inputs


@pytest.fixture
def pforzheim_push_converter(mocked_config_helper: Mock, request_helper: RequestHelper) -> PforzheimPushConverter:
    return PforzheimPushConverter(config_helper=mocked_config_helper, request_helper=request_helper)


class PforzheimPushConverterTest:
    @staticmethod
    def test_get_static_parking_sites(pforzheim_push_converter: PforzheimPushConverter):
        with get_data_path('pforzheim.json').open() as reutlingen_file:
            pforzheim_data = json.loads(reutlingen_file.read())

        static_parking_site_inputs, import_parking_site_exceptions = pforzheim_push_converter.handle_json(
            pforzheim_data,
        )

        assert len(static_parking_site_inputs) == 15
        assert len(import_parking_site_exceptions) == 0

        validate_static_parking_site_inputs(static_parking_site_inputs)
