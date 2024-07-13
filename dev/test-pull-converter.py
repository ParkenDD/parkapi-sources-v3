"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import argparse
import json
import os
import sys
from pathlib import Path

from validataclass.exceptions import ValidationError

sys.path.append(str(Path(Path(__file__).parent.parent, 'src')))  # noqa: E402

from parkapi_sources import ParkAPISources
from parkapi_sources.converters.base_converter.pull import PullConverter
from parkapi_sources.util import DefaultJSONEncoder


def main():
    parser = argparse.ArgumentParser(
        prog='ParkAPI-Sources Test Script',
        description='This script helps to develop ParkAPI-Sources converter',
    )
    parser.add_argument('source_uid')
    args = parser.parse_args()
    source_uid: str = args.source_uid

    config = dict(os.environ)
    config['STATIC_GEOJSON_BASE_PATH'] = Path(Path(__file__).parent.parent, 'data')

    parkapi_sources = ParkAPISources(config=config, converter_uids=[source_uid])
    parkapi_sources.check_credentials()

    converter: PullConverter = parkapi_sources.converter_by_uid[source_uid]  # type: ignore

    static_parking_site_inputs, static_import_parking_site_exceptions = converter.get_static_parking_sites()
    realtime_parking_site_inputs, realtime_import_parking_site_exceptions = converter.get_realtime_parking_sites()

    print('### static data ###')  # noqa: T201
    for static_parking_site_input in static_parking_site_inputs:
        print(json.dumps(filter_none(static_parking_site_input.to_dict()), indent=2, cls=DefaultJSONEncoder))  # noqa: T201

    print('### realtime data ###')  # noqa: T201
    for realtime_parking_site_input in realtime_parking_site_inputs:
        print(json.dumps(filter_none(realtime_parking_site_input.to_dict()), indent=2, cls=DefaultJSONEncoder))  # noqa: T201

    print(f'static_parking_site_errors: {static_import_parking_site_exceptions}')  # noqa: T201
    print(f'realtime_parking_site_errors: {realtime_import_parking_site_exceptions}')  # noqa: T201

    # Additional re-validation if mapping was set up correctly
    for static_parking_site_input in static_parking_site_inputs:
        static_parking_site_dict = json.loads(json.dumps(filter_none(static_parking_site_input.to_dict()), cls=DefaultJSONEncoder))
        try:
            converter.static_parking_site_validator.validate(static_parking_site_dict)
        except ValidationError as e:
            print(f'Invalid mapped static dataset found: {static_parking_site_dict}: {e.to_dict()}')

    for realtime_parking_site_input in realtime_parking_site_inputs:
        realtime_parking_site_dict = json.loads(json.dumps(filter_none(realtime_parking_site_input.to_dict()), cls=DefaultJSONEncoder))
        try:
            converter.realtime_parking_site_validator.validate(realtime_parking_site_dict)
        except ValidationError as e:
            print(f'Invalid mapped realtime dataset found: {realtime_parking_site_dict}: {e.to_dict()}')


def filter_none(data: dict) -> dict:
    return {key: value for key, value in data.items() if value is not None}


if __name__ == '__main__':
    main()
