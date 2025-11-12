"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import json
from unittest.mock import Mock

from parkapi_sources.converters import ParkRaumCheckKehlPushConverter, ParkRaumCheckSachsenheimPushConverter
from parkapi_sources.util import RequestHelper
from tests.converters.helper import get_data_path, validate_static_parking_site_inputs


class ParkRaumCheckSachsenheimPushConverterTest:
    @staticmethod
    def test_get_static_parking_sites(mocked_config_helper: Mock, request_helper: RequestHelper):
        with get_data_path('park_raum_check_sachsenheim.geojson').open() as sachsenheim_file:
            sachsenheim_data = json.loads(sachsenheim_file.read())

        converter = ParkRaumCheckSachsenheimPushConverter(
            config_helper=mocked_config_helper,
            request_helper=request_helper,
        )

        static_parking_site_inputs, import_parking_site_exceptions = converter.handle_json(sachsenheim_data)

        assert len(static_parking_site_inputs) == 38
        assert len(import_parking_site_exceptions) == 0

        validate_static_parking_site_inputs(static_parking_site_inputs)


class ParkRaumCheckKehlPushConverterTest:
    @staticmethod
    def test_get_static_parking_sites(mocked_config_helper: Mock, request_helper: RequestHelper):
        with get_data_path('park_raum_check_kehl.geojson').open() as sachsenheim_file:
            sachsenheim_data = json.loads(sachsenheim_file.read())

        converter = ParkRaumCheckKehlPushConverter(config_helper=mocked_config_helper, request_helper=request_helper)

        static_parking_site_inputs, import_parking_site_exceptions = converter.handle_json(sachsenheim_data)

        assert len(static_parking_site_inputs) == 234
        assert len(import_parking_site_exceptions) == 0

        validate_static_parking_site_inputs(static_parking_site_inputs)
