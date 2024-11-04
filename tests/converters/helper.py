"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import json
from pathlib import Path
from typing import TYPE_CHECKING

from validataclass.validators import DataclassValidator

from parkapi_sources.models import RealtimeParkingSiteInput, StaticParkingSiteInput
from parkapi_sources.util import DefaultJSONEncoder

if TYPE_CHECKING:
    from requests_mock.request import Request
    from requests_mock.response import Context


def get_data_path(filename: str) -> Path:
    return Path(Path(__file__).parent, 'data', filename)


def static_geojson_callback(request: 'Request', context: 'Context'):
    source_uid: str = request.path[1:-8]
    geojson_path = Path(Path(__file__).parent.parent.parent, 'data', f'{source_uid}.geojson')

    # If the GeoJSON does not exist: return an HTTP 404
    if not geojson_path.exists():
        context.status_code = 404
        return {'error': {'code': 'not_found', 'message': f'Source {source_uid} not found.'}}

    # If it exists: load the file and return it
    with geojson_path.open() as geojson_file:
        geojson_data = geojson_file.read()

    return json.loads(geojson_data)


def filter_none(data: dict) -> dict:
    return {key: value for key, value in data.items() if value is not None}


def validate_static_parking_site_inputs(static_parking_site_inputs: list[StaticParkingSiteInput]):
    validator = DataclassValidator(StaticParkingSiteInput)

    for static_parking_site_input in static_parking_site_inputs:
        assert static_parking_site_input.static_data_updated_at.tzinfo is not None
        assert isinstance(static_parking_site_input.uid, str)
        parking_site_dict = json.loads(
            json.dumps(filter_none(static_parking_site_input.to_dict()), cls=DefaultJSONEncoder)
        )
        validator.validate(parking_site_dict)


def validate_realtime_parking_site_inputs(realtime_parking_site_inputs: list[RealtimeParkingSiteInput]):
    validator = DataclassValidator(RealtimeParkingSiteInput)

    for realtime_parking_site_input in realtime_parking_site_inputs:
        assert realtime_parking_site_input.realtime_data_updated_at.tzinfo is not None
        assert isinstance(realtime_parking_site_input.uid, str)
        parking_site_dict = json.loads(
            json.dumps(filter_none(realtime_parking_site_input.to_dict()), cls=DefaultJSONEncoder)
        )
        validator.validate(parking_site_dict)
