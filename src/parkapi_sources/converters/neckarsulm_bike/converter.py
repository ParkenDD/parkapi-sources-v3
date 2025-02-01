"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import csv
from datetime import datetime, timezone
from io import StringIO

import pyproj
from validataclass.exceptions import ValidationError

from parkapi_sources.converters.base_converter.push import CsvConverter
from parkapi_sources.exceptions import ImportParkingSiteException
from parkapi_sources.models import RealtimeParkingSiteInput, SourceInfo, StaticParkingSiteInput


class NeckarsulmBikePushConverter(CsvConverter):
    proj: pyproj.Proj = pyproj.Proj(proj='utm', zone=32, ellps='WGS84', preserve_units=True)

    source_info = SourceInfo(
        uid='neckarsulm_bike',
        name='Stadt Neckarsulm: Fahrad-Abstellanlagen',
        public_url='https://www.neckarsulm.de',
        has_realtime_data=False,
    )

    header_mapping: dict[str, str] = {
        'id': 'uid',
        'gebiet': 'name',
        'anzahl': 'capacity',
        'lage': 'additional_name',
        'eigentuemer': 'operator_name',
        'X': 'lon',
        'y': 'lat',
    }

    def handle_csv_string(
        self,
        data: StringIO,
    ) -> tuple[list[StaticParkingSiteInput | RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        return self.handle_csv(list(csv.reader(data, dialect='unix', delimiter=',')))

    def handle_csv(self, data: list[list]) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        static_parking_site_inputs: list[StaticParkingSiteInput] = []
        static_parking_site_errors: list[ImportParkingSiteException] = []

        mapping: dict[str, int] = self.get_mapping_by_header(self.header_mapping, data[0])

        # We start at row 2, as the first one is our header
        for row in data[1:]:
            input_dict: dict[str, str] = {
                'purpose': 'BIKE',
                'type': 'OTHER',
                'has_realtime_data': False,
                'static_data_updated_at': datetime.now(tz=timezone.utc).isoformat(),
            }
            for field in self.header_mapping.values():
                input_dict[field] = row[mapping[field]]

            if input_dict['name'] and input_dict['additional_name']:
                input_dict['name'] = f'{input_dict["name"]}, {input_dict["additional_name"]}'
            elif input_dict['additional_name']:
                input_dict['name'] = input_dict['additional_name']

            # Convert geo-coordinates
            if input_dict['lat'] and input_dict['lon']:
                coordinates = self.proj(float(input_dict['lon']), float(input_dict['lat']), inverse=True)
                input_dict['lat'] = coordinates[1]
                input_dict['lon'] = coordinates[0]

            try:
                static_parking_site_inputs.append(self.static_parking_site_validator.validate(input_dict))
            except ValidationError as e:
                static_parking_site_errors.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=input_dict.get('id'),
                        message=f'validation error for {input_dict}: {e.to_dict()}',
                    ),
                )
                continue

        return static_parking_site_inputs, static_parking_site_errors
