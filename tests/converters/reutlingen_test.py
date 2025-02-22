"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from io import StringIO
from unittest.mock import Mock

import pytest

from parkapi_sources.converters.reutlingen import ReutlingenPushConverter
from parkapi_sources.util import RequestHelper
from tests.converters.helper import get_data_path, validate_static_parking_site_inputs


@pytest.fixture
def reutlingen_push_converter(mocked_config_helper: Mock, request_helper: RequestHelper) -> ReutlingenPushConverter:
    return ReutlingenPushConverter(config_helper=mocked_config_helper, request_helper=request_helper)


class ReutlingenPushConverterTest:
    @staticmethod
    def test_get_static_parking_sites(reutlingen_push_converter: ReutlingenPushConverter):
        with get_data_path('reutlingen.csv').open() as reutlingen_file:
            reutlingen_data = StringIO(reutlingen_file.read())

        static_parking_site_inputs, import_parking_site_exceptions = reutlingen_push_converter.handle_csv_string(
            reutlingen_data,
        )

        assert len(static_parking_site_inputs) == 12, 'There should be 12 parking sites'
        assert len(import_parking_site_exceptions) == 102, 'There should be 102 exceptions'

        validate_static_parking_site_inputs(static_parking_site_inputs)
