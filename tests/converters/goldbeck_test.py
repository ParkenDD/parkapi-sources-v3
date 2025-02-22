"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from unittest.mock import Mock

import pytest
from openpyxl.reader.excel import load_workbook

from parkapi_sources.converters import GoldbeckPushConverter
from parkapi_sources.util import RequestHelper
from tests.converters.helper import get_data_path, validate_static_parking_site_inputs


@pytest.fixture
def goldbeck_push_converter(mocked_config_helper: Mock, request_helper: RequestHelper) -> GoldbeckPushConverter:
    return GoldbeckPushConverter(config_helper=mocked_config_helper, request_helper=request_helper)


class GoldbeckPushConverterTest:
    @staticmethod
    def test_get_static_parking_sites(goldbeck_push_converter: GoldbeckPushConverter):
        workbook = load_workbook(filename=str(get_data_path('goldbeck.xlsx').absolute()))

        static_parking_site_inputs, import_parking_site_exceptions = goldbeck_push_converter.handle_xlsx(workbook)

        assert len(static_parking_site_inputs) == 10
        assert len(import_parking_site_exceptions) == 1

        validate_static_parking_site_inputs(static_parking_site_inputs)
