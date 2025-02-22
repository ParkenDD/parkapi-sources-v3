"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import json
from unittest.mock import Mock

import pytest

from parkapi_sources.converters.mannheim_buchen import MannheimPushConverter
from parkapi_sources.models import RealtimeParkingSiteInput, StaticParkingSiteInput
from parkapi_sources.util import RequestHelper
from tests.converters.helper import (
    get_data_path,
    validate_realtime_parking_site_inputs,
    validate_static_parking_site_inputs,
)


@pytest.fixture
def mannheim_push_converter(mocked_config_helper: Mock, request_helper: RequestHelper) -> MannheimPushConverter:
    return MannheimPushConverter(config_helper=mocked_config_helper, request_helper=request_helper)


class MannheimPullConverterTest:
    @staticmethod
    def test_get_parking_sites(mannheim_push_converter: MannheimPushConverter):
        # TODO: set proper test files as soon as we get them
        with get_data_path('mannheim.json').open('br') as json_file:
            json_data = json.load(json_file)

        parking_site_inputs, import_parking_site_exceptions = mannheim_push_converter.handle_json(json_data)

        assert len(parking_site_inputs) == len(json_data) * 2, 'There should be two parking sites per input dataset.'
        assert len(import_parking_site_exceptions) == 0, 'There should be no exceptions'

        validate_static_parking_site_inputs([
            item for item in parking_site_inputs if isinstance(item, StaticParkingSiteInput)
        ])
        validate_realtime_parking_site_inputs([
            item for item in parking_site_inputs if isinstance(item, RealtimeParkingSiteInput)
        ])
