"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import json
from unittest.mock import Mock

import pytest

from parkapi_sources.converters import RadolfzellPushConverter
from parkapi_sources.util import RequestHelper
from tests.converters.helper import get_data_path, validate_static_parking_site_inputs


@pytest.fixture
def radolfzell_push_converter(mocked_config_helper: Mock, request_helper: RequestHelper) -> RadolfzellPushConverter:
    return RadolfzellPushConverter(config_helper=mocked_config_helper, request_helper=request_helper)


class RadolfzellPushConverterTest:
    @staticmethod
    def test_get_static_parking_sites(radolfzell_push_converter: RadolfzellPushConverter):
        with get_data_path('radolfzell.geojson').open() as radolfzell_file:
            radolfzell_data = json.loads(radolfzell_file.read())

        static_parking_site_inputs, import_parking_site_exceptions = radolfzell_push_converter.handle_json(
            radolfzell_data,
        )
        assert len(static_parking_site_inputs) == 1142
        assert len(import_parking_site_exceptions) == 0

        validate_static_parking_site_inputs(static_parking_site_inputs)
