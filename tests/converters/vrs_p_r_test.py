"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from unittest.mock import Mock

import pytest
from openpyxl.reader.excel import load_workbook

from parkapi_sources.converters import VrsParkAndRidePushConverter
from parkapi_sources.util import RequestHelper
from tests.converters.helper import get_data_path, validate_static_parking_site_inputs


@pytest.fixture
def vrs_p_r_push_converter(mocked_config_helper: Mock, request_helper: RequestHelper) -> VrsParkAndRidePushConverter:
    return VrsParkAndRidePushConverter(config_helper=mocked_config_helper, request_helper=request_helper)


class VrsParkAndRidePushConverterTest:
    @staticmethod
    def test_get_static_parking_sites(vrs_p_r_push_converter: VrsParkAndRidePushConverter):
        workbook = load_workbook(filename=str(get_data_path('vrs_p_r.xlsx').absolute()))

        static_parking_site_inputs, import_parking_site_exceptions = vrs_p_r_push_converter.handle_xlsx(workbook)

        assert len(static_parking_site_inputs) == 221
        assert len(import_parking_site_exceptions) == 0

        validate_static_parking_site_inputs(static_parking_site_inputs)
