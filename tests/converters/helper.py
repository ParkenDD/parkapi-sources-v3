"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import json
from pathlib import Path
from typing import TYPE_CHECKING

from opening_hours import OpeningHours
from validataclass.validators import DataclassValidator

from parkapi_sources.models import (
    ExternalIdentifierInput,
    ParkingSiteRestrictionInput,
    ParkingSpotRestrictionInput,
    RealtimeParkingSiteInput,
    RealtimeParkingSpotInput,
    StaticParkingSiteInput,
    StaticParkingSpotInput,
)
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

    uids: list[str] = []
    for static_parking_site_input in static_parking_site_inputs:
        assert static_parking_site_input.uid not in uids, 'UID not unique'
        uids.append(static_parking_site_input.uid)

        if static_parking_site_input.restrictions:
            for restriction in static_parking_site_input.restrictions:
                assert isinstance(restriction, ParkingSiteRestrictionInput)

        if static_parking_site_input.external_identifiers:
            for external_identifier in static_parking_site_input.external_identifiers:
                assert isinstance(external_identifier, ExternalIdentifierInput)

        if static_parking_site_input.static_data_updated_at is not None:
            assert static_parking_site_input.static_data_updated_at.tzinfo is not None

        assert isinstance(static_parking_site_input.uid, str)

        if static_parking_site_input.opening_hours:
            OpeningHours(static_parking_site_input.opening_hours)

        parking_site_dict = json.loads(
            json.dumps(filter_none(static_parking_site_input.to_dict()), cls=DefaultJSONEncoder),
        )
        validator.validate(parking_site_dict)


def validate_realtime_parking_site_inputs(realtime_parking_site_inputs: list[RealtimeParkingSiteInput]):
    validator = DataclassValidator(RealtimeParkingSiteInput)

    for realtime_parking_site_input in realtime_parking_site_inputs:
        if realtime_parking_site_input.restrictions:
            for restriction in realtime_parking_site_input.restrictions:
                assert isinstance(restriction, ParkingSiteRestrictionInput)

        assert realtime_parking_site_input.realtime_data_updated_at.tzinfo is not None
        assert isinstance(realtime_parking_site_input.uid, str)

        parking_site_dict = json.loads(
            json.dumps(filter_none(realtime_parking_site_input.to_dict()), cls=DefaultJSONEncoder),
        )
        validator.validate(parking_site_dict)


def validate_static_parking_spot_inputs(static_parking_spot_inputs: list[StaticParkingSpotInput]):
    validator = DataclassValidator(StaticParkingSpotInput)

    for static_parking_spot_input in static_parking_spot_inputs:
        if static_parking_spot_input.restrictions:
            for restriction in static_parking_spot_input.restrictions:
                assert isinstance(restriction, ParkingSpotRestrictionInput)

        assert static_parking_spot_input.static_data_updated_at.tzinfo is not None
        assert isinstance(static_parking_spot_input.uid, str)

        parking_slot_dict = json.loads(
            json.dumps(filter_none(static_parking_spot_input.to_dict()), cls=DefaultJSONEncoder)
        )
        validator.validate(parking_slot_dict)


def validate_realtime_parking_spot_inputs(static_parking_slot_inputs: list[RealtimeParkingSpotInput]):
    validator = DataclassValidator(RealtimeParkingSpotInput)

    for realtime_parking_spot_input in static_parking_slot_inputs:
        assert realtime_parking_spot_input.realtime_data_updated_at.tzinfo is not None
        assert isinstance(realtime_parking_spot_input.uid, str)

        parking_spot_dict = json.loads(
            json.dumps(filter_none(realtime_parking_spot_input.to_dict()), cls=DefaultJSONEncoder)
        )
        validator.validate(parking_spot_dict)
